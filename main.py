from scipy.optimize import linprog
import csv
import matplotlib.pyplot as plt


# =========================================================
# DATA LOADING
# =========================================================

def load_suppliers(filename):
    supplier_capacity = {}

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            capacity = int(row["capacity"])

            if capacity < 0:
                print("Invalid supplier capacity:", row["supplier"])
                raise SystemExit

            supplier_capacity[row["supplier"]] = capacity

    return supplier_capacity


def load_customers(filename):
    customer_demand = {}

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            demand = int(row["demand"])

            if demand < 0:
                print("Invalid customer demand:", row["customer"])
                raise SystemExit

            customer_demand[row["customer"]] = demand

    return customer_demand


def load_shipping_costs(filename):
    shipping_cost = {}

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            route = (
                row["supplier"],
                row["customer"]
            )

            shipping_cost[route] = int(row["cost"])

    return shipping_cost


# =========================================================
# MODEL BUILDING
# =========================================================

def generate_routes(suppliers, customers):
    routes = []

    for supplier in suppliers:
        for customer in customers:
            routes.append(
                (supplier, customer)
            )

    return routes


def build_cost_vector(routes, shipping_cost):
    cost_vector = []

    for route in routes:
        cost_vector.append(
            shipping_cost[route]
        )

    return cost_vector


def build_supplier_matrix(suppliers, routes):
    A_ub = []

    for supplier in suppliers:
        row = []

        for route in routes:
            if route[0] == supplier:
                row.append(1)
            else:
                row.append(0)

        A_ub.append(row)

    return A_ub


def build_customer_matrix(customers, routes):
    A_eq = []

    for customer in customers:
        row = []

        for route in routes:
            if route[1] == customer:
                row.append(1)
            else:
                row.append(0)

        A_eq.append(row)

    return A_eq


def build_supplier_limits(
    suppliers,
    supplier_capacity
):
    b_ub = []

    for supplier in suppliers:
        b_ub.append(
            supplier_capacity[supplier]
        )

    return b_ub


def build_customer_requirements(
    customers,
    customer_demand
):
    b_eq = []

    for customer in customers:
        b_eq.append(
            customer_demand[customer]
        )

    return b_eq


# =========================================================
# OPTIMIZATION
# =========================================================

def solve_transportation_model(
    cost_vector,
    A_ub,
    b_ub,
    A_eq,
    b_eq
):
    result = linprog(
        c=cost_vector,
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=A_eq,
        b_eq=b_eq
    )

    return result


def solve_scenario(
    suppliers,
    customers,
    routes,
    shipping_cost,
    supplier_capacity,
    customer_demand
):
    cost_vector = build_cost_vector(
        routes,
        shipping_cost
    )

    A_ub = build_supplier_matrix(
        suppliers,
        routes
    )

    b_ub = build_supplier_limits(
        suppliers,
        supplier_capacity
    )

    A_eq = build_customer_matrix(
        customers,
        routes
    )

    b_eq = build_customer_requirements(
        customers,
        customer_demand
    )

    result = solve_transportation_model(
        cost_vector,
        A_ub,
        b_ub,
        A_eq,
        b_eq
    )

    return result


# =========================================================
# SOLUTION VALIDATION
# =========================================================

def validate_solution(
    shipments,
    suppliers,
    customers,
    supplier_capacity,
    customer_demand,
    result
):
    validation_passed = True
    tolerance = 1e-9

    # Supplier capacity checks
    for supplier in suppliers:
        total_shipped = 0

        for customer in customers:
            total_shipped += shipments[
                (supplier, customer)
            ]

        if (
            total_shipped
            > supplier_capacity[supplier] + tolerance
        ):
            print(
                "Supplier capacity violated:",
                supplier
            )

            validation_passed = False

    # Customer demand checks
    for customer in customers:
        total_received = 0

        for supplier in suppliers:
            total_received += shipments[
                (supplier, customer)
            ]

        if (
            abs(
                total_received
                - customer_demand[customer]
            )
            > tolerance
        ):
            print(
                "Supply does not meet customer's demand:",
                customer
            )

            validation_passed = False

    # Nonnegative shipment check
    for quantity in result.x:
        if quantity < -tolerance:
            print(
                "Negative shipment detected!"
            )

            validation_passed = False

    return validation_passed


# =========================================================
# COST VERIFICATION
# =========================================================

def calculate_total_cost(
    routes,
    shipments,
    shipping_cost
):
    total_cost = 0

    for route in routes:
        total_cost += (
            shipments[route]
            * shipping_cost[route]
        )

    return total_cost


# =========================================================
# SUPPLIER DISRUPTION
# =========================================================

def apply_supplier_disruption(
    supplier_capacity,
    supplier,
    reduction_percent
):
    disrupted_capacity = (
        supplier_capacity.copy()
    )

    original_capacity = (
        disrupted_capacity[supplier]
    )

    disrupted_capacity[supplier] = (
        original_capacity
        * (1 - reduction_percent)
    )

    return disrupted_capacity


# =========================================================
# RESILIENCE STRESS TEST
# =========================================================

def run_resilience_stress_test(
    suppliers,
    customers,
    routes,
    shipping_cost,
    supplier_capacity,
    customer_demand,
    baseline_cost
):
    disruption_levels = [
        0.10,
        0.25,
        0.50,
        0.75,
        1.00
    ]

    stress_test_results = []

    for supplier in suppliers:

        for reduction in disruption_levels:

            disrupted_capacity = (
                apply_supplier_disruption(
                    supplier_capacity,
                    supplier,
                    reduction
                )
            )

            result = solve_scenario(
                suppliers,
                customers,
                routes,
                shipping_cost,
                disrupted_capacity,
                customer_demand
            )

            if result.success:
                disrupted_cost = result.fun

                cost_increase = (
                    disrupted_cost
                    - baseline_cost
                )

                percent_increase = (
                    cost_increase
                    / baseline_cost
                ) * 100

                stress_test_results.append({
                    "supplier": supplier,
                    "reduction": reduction,
                    "feasible": True,
                    "cost": disrupted_cost,
                    "cost_increase": cost_increase,
                    "percent_increase": percent_increase
                })

            else:
                stress_test_results.append({
                    "supplier": supplier,
                    "reduction": reduction,
                    "feasible": False,
                    "cost": None,
                    "cost_increase": None,
                    "percent_increase": None
                })

    return stress_test_results


# =========================================================
# RESILIENCE SUMMARY
# =========================================================

def summarize_resilience_results(
    stress_test_results
):
    feasible_scenarios = [
        scenario
        for scenario in stress_test_results
        if scenario["feasible"]
    ]

    infeasible_scenarios = [
        scenario
        for scenario in stress_test_results
        if not scenario["feasible"]
    ]

    print("\nResilience Summary")

    # Largest feasible cost increase
    if feasible_scenarios:
        worst_feasible = max(
            feasible_scenarios,
            key=lambda scenario:
            scenario["percent_increase"]
        )

        print(
            "Largest feasible cost increase:",
            "Supplier",
            worst_feasible["supplier"],
            "| Capacity loss:",
            worst_feasible["reduction"] * 100,
            "%",
            "| Cost increase:",
            round(
                worst_feasible["cost_increase"],
                2
            ),
            "| Percent increase:",
            round(
                worst_feasible["percent_increase"],
                2
            ),
            "%"
        )

    # First infeasible disruption level
    if infeasible_scenarios:
        print("\nInfeasibility Thresholds")

        first_infeasible_by_supplier = {}

        for scenario in infeasible_scenarios:
            supplier = scenario["supplier"]

            if (
                supplier
                not in first_infeasible_by_supplier
            ):
                first_infeasible_by_supplier[
                    supplier
                ] = scenario["reduction"]

        for (
            supplier,
            reduction
        ) in first_infeasible_by_supplier.items():

            print(
                "Supplier",
                supplier,
                "| First infeasible capacity loss:",
                reduction * 100,
                "%"
            )

    # Largest disruption with no cost increase
    print("\nZero-Cost Resilience")

    unique_suppliers = sorted({
        scenario["supplier"]
        for scenario in stress_test_results
    })

    for supplier in unique_suppliers:

        zero_cost_scenarios = [
            scenario
            for scenario in stress_test_results
            if (
                scenario["supplier"] == supplier
                and scenario["feasible"]
                and abs(
                    scenario["cost_increase"]
                ) <= 1e-9
            )
        ]

        if zero_cost_scenarios:
            highest_zero_cost = max(
                zero_cost_scenarios,
                key=lambda scenario:
                scenario["reduction"]
            )

            print(
                "Supplier",
                supplier,
                "| No cost impact through:",
                highest_zero_cost[
                    "reduction"
                ] * 100,
                "% capacity loss"
            )


# =========================================================
# SENSITIVITY / SHADOW PRICE ANALYSIS
# =========================================================

def analyze_sensitivity(
    result,
    suppliers,
    customers
):
    tolerance = 1e-9

    print("\nSensitivity Analysis")

    print(
        "\nSupplier Capacity Constraints"
    )

    for index, supplier in enumerate(
        suppliers
    ):
        slack = (
            result.ineqlin.residual[index]
        )

        marginal = (
            result.ineqlin.marginals[index]
        )

        capacity_value = -marginal

        if abs(slack) <= tolerance:
            status = "BINDING"
        else:
            status = "NON-BINDING"

        print(
            "Supplier",
            supplier,
            "| Status:",
            status,
            "| Unused capacity:",
            round(slack, 2),
            "| Value of +1 capacity:",
            round(capacity_value, 2)
        )

    print(
        "\nCustomer Demand Constraints"
    )

    for index, customer in enumerate(
        customers
    ):
        marginal = (
            result.eqlin.marginals[index]
        )

        print(
            "Customer",
            customer,
            "| Cost of +1 demand:",
            round(marginal, 2)
        )


# =========================================================
# TEXT OUTPUT
# =========================================================

def print_solution(
    routes,
    shipments,
    total_cost,
    validation_passed,
    suppliers,
    customers
):
    print(
        "\nNetwork size:",
        len(suppliers),
        "suppliers,",
        len(customers),
        "customers"
    )

    print(
        "Decision variables:",
        len(routes)
    )

    print(
        "\nOptimal Shipment Plan"
    )

    for route in routes:
        quantity = shipments[route]

        if quantity > 0:
            supplier = route[0]
            customer = route[1]

            print(
                "Supplier",
                supplier,
                "-> Customer",
                customer,
                ":",
                round(quantity, 2)
            )

    print(
        "\nMinimum total cost:",
        round(total_cost, 2)
    )

    if validation_passed:
        print(
            "Validation: PASSED"
        )
    else:
        print(
            "Validation: FAILED"
        )


def print_stress_test_results(
    stress_test_results
):
    print(
        "\nResilience Stress Test"
    )

    for scenario in stress_test_results:
        supplier = scenario["supplier"]

        reduction = (
            scenario["reduction"]
            * 100
        )

        if scenario["feasible"]:
            print(
                "Supplier",
                supplier,
                "| Capacity loss:",
                reduction,
                "%",
                "| Cost:",
                round(
                    scenario["cost"],
                    2
                ),
                "| Increase:",
                round(
                    scenario["cost_increase"],
                    2
                ),
                "| Percent increase:",
                round(
                    scenario[
                        "percent_increase"
                    ],
                    2
                ),
                "%"
            )

        else:
            print(
                "Supplier",
                supplier,
                "| Capacity loss:",
                reduction,
                "%",
                "| INFEASIBLE"
            )


# =========================================================
# RESILIENCE VISUALIZATION
# =========================================================

def plot_resilience_results(
    stress_test_results,
    suppliers,
    baseline_cost
):
    plt.figure(
        figsize=(10, 6)
    )

    for supplier in suppliers:
        reductions = []
        costs = []

        for scenario in stress_test_results:

            if (
                scenario["supplier"]
                == supplier
                and scenario["feasible"]
            ):
                reductions.append(
                    scenario["reduction"]
                    * 100
                )

                costs.append(
                    scenario["cost"]
                )

        plt.plot(
            reductions,
            costs,
            marker="o",
            label="Supplier " + supplier
        )

    plt.axhline(
        y=baseline_cost,
        linestyle="--",
        label="Baseline Cost"
    )

    plt.xlabel(
        "Supplier Capacity Loss (%)"
    )

    plt.ylabel(
        "Optimal Transportation Cost"
    )

    plt.title(
        "Supply Chain Resilience Stress Test"
    )

    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        "outputs/resilience_stress_test.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()


# =========================================================
# SHIPMENT NETWORK VISUALIZATION
# =========================================================

def plot_shipment_network(
    suppliers,
    customers,
    shipments
):
    plt.figure(
        figsize=(12, 7)
    )

    supplier_x = 0
    customer_x = 10

    supplier_positions = {}
    customer_positions = {}

    # Supplier positions
    for index, supplier in enumerate(
        suppliers
    ):
        supplier_y = (
            len(suppliers)
            - index
        )

        supplier_positions[supplier] = (
            supplier_x,
            supplier_y
        )

        plt.scatter(
            supplier_x,
            supplier_y,
            s=1200
        )

        plt.text(
            supplier_x,
            supplier_y,
            "Supplier " + supplier,
            ha="center",
            va="center"
        )

    # Customer positions
    for index, customer in enumerate(
        customers
    ):
        customer_y = (
            len(customers)
            - index
        )

        customer_positions[customer] = (
            customer_x,
            customer_y
        )

        plt.scatter(
            customer_x,
            customer_y,
            s=1200
        )

        plt.text(
            customer_x,
            customer_y,
            "Customer " + customer,
            ha="center",
            va="center"
        )

    # Draw active routes
    for route, quantity in (
        shipments.items()
    ):

        if quantity > 0:

            supplier = route[0]
            customer = route[1]

            supplier_position = (
                supplier_positions[
                    supplier
                ]
            )

            customer_position = (
                customer_positions[
                    customer
                ]
            )

            x_values = [
                supplier_position[0],
                customer_position[0]
            ]

            y_values = [
                supplier_position[1],
                customer_position[1]
            ]

            line_width = (
                1
                + quantity / 25
            )

            plt.plot(
                x_values,
                y_values,
                linewidth=line_width
            )

            midpoint_x = (
                supplier_position[0]
                + customer_position[0]
            ) / 2

            midpoint_y = (
                supplier_position[1]
                + customer_position[1]
            ) / 2

            label_offset = 0.12

            if (
                supplier_position[1]
                <= customer_position[1]
            ):
                label_y = (
                    midpoint_y
                    + label_offset
                )

            else:
                label_y = (
                    midpoint_y
                    - label_offset
                )

            plt.text(
                midpoint_x,
                label_y,
                str(
                    round(quantity, 1)
                ),
                ha="center",
                va="center",
                bbox={
                    "facecolor": "white",
                    "alpha": 0.8,
                    "edgecolor": "none"
                }
            )

    plt.title(
        "Optimized Supply Chain Shipment Network"
    )

    plt.xlim(
        -2,
        12
    )

    plt.axis(
        "off"
    )

    plt.tight_layout()

    plt.savefig(
        "outputs/optimized_shipment_network.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()


# =========================================================
# MAIN PROGRAM
# =========================================================

def main():

    # -----------------------------------------------------
    # Load network data
    # -----------------------------------------------------

    supplier_capacity = load_suppliers(
        "suppliers_large.csv"
    )

    customer_demand = load_customers(
        "customers_large.csv"
    )

    shipping_cost = load_shipping_costs(
        "shipping_costs_large.csv"
    )

    # -----------------------------------------------------
    # Aggregate feasibility check
    # -----------------------------------------------------

    total_supply = sum(
        supplier_capacity.values()
    )

    total_demand = sum(
        customer_demand.values()
    )

    if total_supply < total_demand:
        print(
            "Not enough supply to meet total customer demand!"
        )

        raise SystemExit

    # -----------------------------------------------------
    # Build supplier/customer network
    # -----------------------------------------------------

    suppliers = list(
        supplier_capacity.keys()
    )

    customers = list(
        customer_demand.keys()
    )

    routes = generate_routes(
        suppliers,
        customers
    )

    # Validate that every route has a shipping cost
    for route in routes:

        if route not in shipping_cost:
            print(
                "Missing shipping cost for route:",
                route
            )

            raise SystemExit

    # -----------------------------------------------------
    # Build baseline LP
    # -----------------------------------------------------

    cost_vector = build_cost_vector(
        routes,
        shipping_cost
    )

    A_ub = build_supplier_matrix(
        suppliers,
        routes
    )

    b_ub = build_supplier_limits(
        suppliers,
        supplier_capacity
    )

    A_eq = build_customer_matrix(
        customers,
        routes
    )

    b_eq = build_customer_requirements(
        customers,
        customer_demand
    )

    # -----------------------------------------------------
    # Solve baseline network
    # -----------------------------------------------------

    result = solve_transportation_model(
        cost_vector,
        A_ub,
        b_ub,
        A_eq,
        b_eq
    )

    if not result.success:
        print(
            "Optimization failed:",
            result.message
        )

        raise SystemExit

    shipments = dict(
        zip(
            routes,
            result.x
        )
    )

    # -----------------------------------------------------
    # Validate baseline solution
    # -----------------------------------------------------

    validation_passed = (
        validate_solution(
            shipments,
            suppliers,
            customers,
            supplier_capacity,
            customer_demand,
            result
        )
    )

    # -----------------------------------------------------
    # Verify objective independently
    # -----------------------------------------------------

    verified_cost = (
        calculate_total_cost(
            routes,
            shipments,
            shipping_cost
        )
    )

    # -----------------------------------------------------
    # Run 25 resilience scenarios
    # -----------------------------------------------------

    stress_test_results = (
        run_resilience_stress_test(
            suppliers,
            customers,
            routes,
            shipping_cost,
            supplier_capacity,
            customer_demand,
            verified_cost
        )
    )

    # -----------------------------------------------------
    # Print baseline solution
    # -----------------------------------------------------

    print_solution(
        routes,
        shipments,
        verified_cost,
        validation_passed,
        suppliers,
        customers
    )

    # -----------------------------------------------------
    # Print resilience analysis
    # -----------------------------------------------------

    print_stress_test_results(
        stress_test_results
    )

    summarize_resilience_results(
        stress_test_results
    )

    # -----------------------------------------------------
    # LP sensitivity / shadow-price analysis
    # -----------------------------------------------------

    analyze_sensitivity(
        result,
        suppliers,
        customers
    )

    # -----------------------------------------------------
    # Visualizations
    # -----------------------------------------------------

    plot_resilience_results(
        stress_test_results,
        suppliers,
        verified_cost
    )

    plot_shipment_network(
        suppliers,
        customers,
        shipments
    )


if __name__ == "__main__":
    main()