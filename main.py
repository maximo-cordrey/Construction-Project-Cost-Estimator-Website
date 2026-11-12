from drafter import *
from dataclasses import dataclass
import math


# Each estimate is one saved material or labor calculation.
@dataclass
class Estimate:
    material_name: str
    quantity: float
    unit: str
    unit_price: float
    total_cost: float


# State keeps information available across all website pages.
@dataclass
class State:
    project_name: str
    current_page: str
    selected_material: str
    estimates: list[Estimate]
    total_cost: float


def update_total_cost(state: State) -> None:
    """Add the costs of all saved estimates."""
    total = 0.0

    for estimate in state.estimates:
        total += estimate.total_cost

    state.total_cost = total


def add_estimate(state: State, name: str, quantity: float,
                 unit: str, unit_price: float,
                 total_cost: float) -> None:
    """Save a new estimate and update the project total."""
    new_estimate = Estimate(
        name, quantity, unit, unit_price, total_cost
    )
    state.estimates.append(new_estimate)
    update_total_cost(state)


# The index route opens the home page when the website starts.
@route
def index(state: State) -> Page:
    """Open the website's home page."""
    return home_page(state)


@route
def home_page(state: State) -> Page:
    """Display the home page and navigation."""
    state.current_page = "Home"

    return Page(state, [
        Header("Project Cost Calculator"),
        "A simple construction project cost estimator.",
        "Enter your project information and estimate "
        "your material and labor costs.",
        HorizontalRule(),
        Header("Your Project"),
        "Current project: " + state.project_name,
        "Enter a project name to begin or update your project:",
        TextBox("project_name", state.project_name),
        Button("Start Project", "start_project"),
        HorizontalRule(),
        Header("Choose a Calculator"),
        Button("Concrete Calculator", "concrete_page"),
        Button("Wood Calculator", "wood_page"),
        Button("Workers Calculator", "workers_page"),
        HorizontalRule(),
        Button("View Project Summary", "summary_page")
    ])


@route
def start_project(state: State, project_name: str) -> Page:
    """Save the project name and begin a new project."""
    if project_name.strip() == "":
        state.project_name = "My Construction Project"
    else:
        state.project_name = project_name.strip()

    state.estimates = []
    state.total_cost = 0.0
    state.selected_material = ""
    return home_page(state)


# CONCRETE CALCULATOR

@route
def concrete_page(state: State) -> Page:
    """Display the concrete calculator form."""
    state.current_page = "Concrete Calculator"

    return Page(state, [
        Header("Concrete Calculator"),
        "Enter the dimensions in feet.",
        "Concrete depth (in feet) should be a decimal, "
        "such as 0.5 for six inches.",
        "Length:",
        TextBox("length", 10.0, "number"),
        "Width:",
        TextBox("width", 10.0, "number"),
        "Depth:",
        TextBox("depth", 0.5, "number"),
        "Price per cubic yard:",
        TextBox("concrete_price", 150.0, "number"),
        Button("Calculate and Save Concrete", "save_concrete"),
        Link("Return Home", "home_page")
    ])


@route
def save_concrete(state: State, length: float, width: float,
                  depth: float, concrete_price: float) -> Page:
    """Calculate concrete volume and save its estimated cost."""
    state.current_page = "Concrete Calculator"

    if length <= 0 or width <= 0 or depth <= 0:
        return Page(state, [
            Header("Invalid Dimensions"),
            "All dimensions must be greater than zero.",
            Link("Try Again", "concrete_page")
        ])

    if concrete_price < 0:
        return Page(state, [
            Header("Invalid Price"),
            "The concrete price cannot be negative.",
            Link("Try Again", "concrete_page")
        ])

    # There are 27 cubic feet in one cubic yard.
    volume_cubic_yards = (length * width * depth) / 27
    total_cost = volume_cubic_yards * concrete_price

    state.selected_material = "Concrete"

    add_estimate(
        state,
        "Concrete",
        volume_cubic_yards,
        "cubic yards",
        concrete_price,
        total_cost
    )

    return Page(state, [
        Header("Concrete Estimate Saved"),
        "Estimated volume: " + str(round(volume_cubic_yards, 2))
        + " cubic yards",
        "Estimated cost: $" + str(round(total_cost, 2)),
        Button("View Project Summary", "summary_page"),
        Link("Return Home", "home_page")
    ])


# WOOD CALCULATOR

@route
def wood_page(state: State) -> Page:
    """Display the wood calculator form."""
    state.current_page = "Wood Calculator"

    return Page(state, [
        Header("Wood Calculator"),
        "Enter the building dimensions in feet.",
        "This calculator estimates wall studs only.",
        "It does not calculate every piece of lumber "
        "needed for a complete building.",
        "Building length:",
        TextBox("building_length", 20.0, "number"),
        "Building width:",
        TextBox("building_width", 15.0, "number"),
        "Wall height:",
        TextBox("wall_height", 8.0, "number"),
        "Choose a lumber type:",
        SelectBox(
            "lumber_type",
            ["2x4", "2x6", "4x4"],
            "2x4"
        ),
        "Price per piece of lumber:",
        TextBox("lumber_price", 5.0, "number"),
        Button("Calculate and Save Wood", "save_wood"),
        Link("Return Home", "home_page")
    ])


@route
def save_wood(state: State, building_length: float,
              building_width: float, wall_height: float,
              lumber_type: str, lumber_price: float) -> Page:
    """Estimate the number and cost of wall studs."""
    state.current_page = "Wood Calculator"

    if (building_length <= 0 or building_width <= 0
            or wall_height <= 0):
        return Page(state, [
            Header("Invalid Dimensions"),
            "All building dimensions must be greater than zero.",
            Link("Try Again", "wood_page")
        ])

    if lumber_price < 0:
        return Page(state, [
            Header("Invalid Price"),
            "The lumber price cannot be negative.",
            Link("Try Again", "wood_page")
        ])

    # Estimate one stud about every 16 inches around the walls.
    perimeter = 2 * (building_length + building_width)
    estimated_studs = math.ceil(perimeter * 12 / 16) + 4

    # Add approximately 10 percent extra for waste.
    estimated_studs = math.ceil(estimated_studs * 1.10)

    total_cost = estimated_studs * lumber_price

    state.selected_material = lumber_type

    add_estimate(
        state,
        "Wood (" + lumber_type + ")",
        estimated_studs,
        "pieces",
        lumber_price,
        total_cost
    )

    return Page(state, [
        Header("Wood Estimate Saved"),
        "Lumber type: " + lumber_type,
        "Estimated number of studs: " + str(estimated_studs),
        "Estimated cost: $" + str(round(total_cost, 2)),
        Button("View Project Summary", "summary_page"),
        Link("Return Home", "home_page")
    ])


# WORKERS CALCULATOR

@route
def workers_page(state: State) -> Page:
    """Display the workers and labor cost calculator."""
    state.current_page = "Workers Calculator"

    return Page(state, [
        Header("Workers Calculator"),
        "Enter the estimated labor information.",
        "Number of workers:",
        TextBox("worker_count", 2, "number"),
        "Hours worked per worker:",
        TextBox("hours_worked", 8.0, "number"),
        "Hourly pay per worker:",
        TextBox("hourly_pay", 20.0, "number"),
        Button("Calculate and Save Labor", "save_workers"),
        Link("Return Home", "home_page")
    ])


@route
def save_workers(state: State, worker_count: int,
                 hours_worked: float,
                 hourly_pay: float) -> Page:
    """Calculate labor hours and save the labor cost."""
    state.current_page = "Workers Calculator"

    if worker_count <= 0:
        return Page(state, [
            Header("Invalid Worker Count"),
            "You must enter at least one worker.",
            Link("Try Again", "workers_page")
        ])

    if hours_worked <= 0:
        return Page(state, [
            Header("Invalid Hours"),
            "Hours worked must be greater than zero.",
            Link("Try Again", "workers_page")
        ])

    if hourly_pay < 0:
        return Page(state, [
            Header("Invalid Hourly Pay"),
            "Hourly pay cannot be negative.",
            Link("Try Again", "workers_page")
        ])

    total_labor_hours = worker_count * hours_worked
    total_cost = total_labor_hours * hourly_pay

    state.selected_material = "Labor"

    add_estimate(
        state,
        "Labor",
        total_labor_hours,
        "worker-hours",
        hourly_pay,
        total_cost
    )

    return Page(state, [
        Header("Labor Estimate Saved"),
        "Number of workers: " + str(worker_count),
        "Total labor hours: " + str(total_labor_hours),
        "Estimated labor cost: $" + str(round(total_cost, 2)),
        Button("View Project Summary", "summary_page"),
        Link("Return Home", "home_page")
    ])


# PROJECT SUMMARY

@route
def summary_page(state: State) -> Page:
    """Display saved estimates and the total project cost."""
    state.current_page = "Project Summary"
    update_total_cost(state)

    content = [
        Header("Project Cost Summary"),
        "Project: " + state.project_name,
        HorizontalRule(),
        Header("Saved Estimates")
    ]

    if len(state.estimates) == 0:
        content.append("No estimates have been saved yet.")
    else:
        # This loop displays every saved Estimate object.
        for estimate in state.estimates:
            content.append(
                estimate.material_name
                + ": "
                + str(round(estimate.quantity, 2))
                + " "
                + estimate.unit
            )
            content.append(
                "Unit price: $"
                + str(round(estimate.unit_price, 2))
            )
            content.append(
                "Total cost: $"
                + str(round(estimate.total_cost, 2))
            )
            content.append(HorizontalRule())

    content.append(
        "TOTAL PROJECT COST: $"
        + str(round(state.total_cost, 2))
    )

    # A simple text-based comparison of the saved costs.
    content.append(Header("Cost Comparison"))

    if state.total_cost > 0:
        for estimate in state.estimates:
            bar_length = int(
                estimate.total_cost / state.total_cost * 30
            )
            content.append(
                estimate.material_name
                + ": "
                + "#" * bar_length
                + " $"
                + str(round(estimate.total_cost, 2))
            )
    else:
        content.append("Save an estimate to see the comparison.")

    content.append(HorizontalRule())
    content.append(Button("Return Home", "home_page"))
    content.append(Button("Start a New Project", "clear_project"))

    return Page(state, content)


# START A NEW PROJECT

@route
def clear_project(state: State) -> Page:
    """Clear the saved estimates and start a fresh project."""
    state.project_name = "New Construction Project"
    state.current_page = "Home"
    state.selected_material = ""
    state.estimates = []
    state.total_cost = 0.0

    return home_page(state)

set_website_title("Project Cost Calculator")
set_site_information(
    author="Maximo Cordrey",
    description="Estimate the cost of a small construction project.",
    sources="Thanks to the Drafter docs, class resourses, and some help from LLMs.",
    planning=["Copy of CS1 Final Project 1: Design(1).pdf", "Copy of CS1 Final Project 1: Design.pdf", "LLM Conversations for CISC Project.pdf"],
    links=["https://github.com/maximo-cordrey/Construction-Project-Cost-Estimator-Website"]
)
hide_debug_information()
set_website_framed(False)

# Start the Drafter website.
start_server(
    State(
        "My Construction Project",
        "Home",
        "",
        [],
        0.0
    )
)

