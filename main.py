# uvicorn main:app --reload

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
from enum import Enum


# Allowed lifecycle states for a ticket.
# Using an Enum:
# - restricts values to known states
# - gives automatic validation
# - improves API docs (/docs)
class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


# Shared fields for a ticket.
# This base model is reused by multiple schemas so we don't repeat ourselves.
# NOTE: This does NOT represent a database table by itself.
class TicketBase(SQLModel):
    title: str
    description: str
    # User-provided urgency, validated to be within a reasonable range
    priority: int = Field(ge=1, le=5)
    # System-controlled lifecycle state (defaults to "open")
    status: TicketStatus = TicketStatus.open


# Database model (ORM).
# This maps directly to a database table and includes a primary key.
# Instances of this class are tracked by the DB session.
class Ticket(TicketBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


# Public response model.
# This defines the exact shape of ticket data returned to clients.
# It includes the database-generated ID but excludes any internal-only fields.
class TicketPublic(TicketBase):
    id: int


# Request model for creating a ticket.
# This represents what a client is allowed to send when creating a ticket.
# Status is intentionally excluded so new tickets always start in a valid state.
class TicketCreate(SQLModel):
    title: str
    description: str
    priority: int = Field(ge=1, le=5)


# Request model for updating a ticket (PATCH).
# All fields are optional so clients can send partial updates.
# Only provided fields will be applied to the existing database record.
class TicketUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    status: TicketStatus | None = None



sqlite_file_name = "database.db"
# SQLAlchemy connection URL for SQLite.
# The triple slash (///) means "use a local file path".
sqlite_url = f"sqlite:///{sqlite_file_name}"

# SQLite is not thread-safe by default.
# FastAPI can handle requests in multiple threads,
# so we disable SQLite's same-thread check.
connect_args = {"check_same_thread": False}

# Create the SQLAlchemy engine.
# The engine is the core object that manages database connections.
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    """
    Create all database tables defined by SQLModel models.

    This reads all classes that inherit from SQLModel with table=True
    (e.g., Ticket) and creates the corresponding tables if they do not exist.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Provide a database session for a single request.

    This function is used as a FastAPI dependency.
    A new session is created for each request and automatically
    closed when the request is finished.
    """
    with Session(engine) as session:
        yield session


# Type alias for injecting a database session into route handlers.
# This avoids repeating Depends(get_session) everywhere.
SessionDep = Annotated[Session, Depends(get_session)]

# Create the FastAPI application instance.
app = FastAPI(
    title="Helpdesk API",
    version="1.0.0",
    description="A small REST API demonstrating CRUD + search + PATCH backed by SQLite."
)


@app.on_event("startup")
def on_startup():
    """
    Run application startup tasks.

    This ensures that the database tables exist
    before the application starts handling requests.
    """
    create_db_and_tables()


@app.get("/")
def root():
    return {
        "service": "helpdesk-api",
        "status": "ok",
        "docs": "/docs"
    }



# Fast API reads the JSON body, uses Pydantic to validate types, and enforce constraints (priority 1-5), and constructs the Python object (JSON to Python)
@app.post("/tickets/", response_model=TicketPublic) # The response_model enforces the type/shape of the object being returned
def add_ticket(ticket: TicketCreate, session: SessionDep) -> TicketPublic:
    # Now we need to convert from TicketCreate (input schema) to Ticket (database model)
    db_ticket = Ticket.model_validate(ticket)
    # The line above does the same as:
    # db_ticket = Ticket(title=ticket.title, description=ticket.description, priority=ticket.priority)
    session.add(db_ticket) # add() tells the session that this object will be inserted into the database
    session.commit() # commit() executes the SQL that adds the object to the database (id is auto generated)
    session.refresh(db_ticket) # refresh() reloads the object from the database into Python memory. This is needed since the Python object may not know about the DB-generated field(s) (id in this case)
    return db_ticket # Fast API looks at the response_model, so it knows the type being returned, and then returns the object (Python to JSON)


# Get all Tickets
@app.get("/tickets/", response_model=list[TicketPublic])
def read_tickets(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Ticket]:
    tickets = session.exec(select(Ticket).offset(offset).limit(limit)).all()
    return tickets


# Get Ticket by id
@app.get("/tickets/{ticket_id}", response_model=TicketPublic)
def query_ticket_by_id(ticket_id: int, session: SessionDep) -> Ticket:
    # Search using the ticket's id, which is the primary key in the DB
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=404, detail=f"Ticket with {ticket_id=} does not exist"
        )
    return ticket

# Search for a ticket via query parameters
@app.get("/tickets/search", response_model=list[TicketPublic])
def query_ticket_by_parameters(
    session: Session = Depends(get_session),
    title: str | None = None,
    description: str | None = None,
    priority: int | None = Query(default=None, ge=1, le=5),
    status: TicketStatus | None = None,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
) -> list[Ticket]:
    stmt = select(Ticket)

    # Build the search query
    # Add filters only if the query param was provided
    if title is not None:
        # Case-insensitive exact match
        stmt = stmt.where(Ticket.title.ilike(title))

    if description is not None:
        stmt = stmt.where(Ticket.description.ilike(description))

    if priority is not None:
        stmt = stmt.where(Ticket.priority == priority)

    if status is not None:
        stmt = stmt.where(Ticket.status == status)

    # Execute the search query
    tickets = session.exec(stmt.offset(offset).limit(limit)).all()
    return tickets


# Update Ticket
@app.patch("/tickets/{ticket_id}", response_model=TicketPublic)
def update_ticket(
    ticket_id: int,
    ticket: TicketUpdate,
    session: SessionDep
):
    # Grab the ticket we want to update from the DB
    ticket_db = session.get(Ticket, ticket_id)
    if not ticket_db:
        raise HTTPException(
            status_code=404, detail=f"Ticket with {ticket_id=} does not exist"
        )
    # Pull ONLY the fields the user actually sent
    ticket_data = ticket.model_dump(exclude_unset=True)
    # Apply changes onto the DB object
    ticket_db.sqlmodel_update(ticket_data)
    session.add(ticket_db)
    session.commit()
    session.refresh(ticket_db)
    return ticket_db


# Delete Ticket
@app.delete("/tickets/{ticket_id}", response_model=TicketPublic)
def delete_ticket(
    ticket_id: int,
    session: SessionDep
) -> TicketPublic:
    # Get the ticket we want to delete from the DB
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=404, detail=f"Ticket with {ticket_id=} does not exist"
        )

    session.delete(ticket)
    session.commit()

    return ticket