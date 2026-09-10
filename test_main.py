import csv
import os
import tempfile
import unittest

from main import (
    load_suppliers,
    load_customers,
    load_shipping_costs,
    generate_routes,
    build_cost_vector,
    build_supplier_matrix,
    build_customer_matrix,
    build_supplier_limits,
    build_customer_requirements,
    solve_transportation_model,
    solve_scenario,
    validate_solution,
    calculate_total_cost,
    apply_supplier_disruption,
    run_resilience_stress_test
)


class TestSupplyChainOptimizer(unittest.TestCase):

    def test_generate_routes(self):
        suppliers = ["A", "B"]
        customers = ["1", "2", "3"]

        routes = generate_routes(
            suppliers,
            customers
        )

        expected_routes = [
            ("A", "1"),
            ("A", "2"),
            ("A", "3"),
            ("B", "1"),
            ("B", "2"),
            ("B", "3")
        ]

        self.assertEqual(
            routes,
            expected_routes
        )


    def test_build_cost_vector(self):
        routes = [
            ("A", "1"),
            ("A", "2"),
            ("B", "1"),
            ("B", "2")
        ]

        shipping_cost = {
            ("A", "1"): 4,
            ("A", "2"): 7,
            ("B", "1"): 6,
            ("B", "2"): 3
        }

        cost_vector = build_cost_vector(
            routes,
            shipping_cost
        )

        expected = [
            4,
            7,
            6,
            3
        ]

        self.assertEqual(
            cost_vector,
            expected
        )


    def test_build_supplier_matrix(self):
        suppliers = [
            "A",
            "B"
        ]

        routes = [
            ("A", "1"),
            ("A", "2"),
            ("B", "1"),
            ("B", "2")
        ]

        matrix = build_supplier_matrix(
            suppliers,
            routes
        )

        expected = [
            [1, 1, 0, 0],
            [0, 0, 1, 1]
        ]

        self.assertEqual(
            matrix,
            expected
        )


    def test_build_customer_matrix(self):
        customers = [
            "1",
            "2"
        ]

        routes = [
            ("A", "1"),
            ("A", "2"),
            ("B", "1"),
            ("B", "2")
        ]

        matrix = build_customer_matrix(
            customers,
            routes
        )

        expected = [
            [1, 0, 1, 0],
            [0, 1, 0, 1]
        ]

        self.assertEqual(
            matrix,
            expected
        )


    def test_build_supplier_limits(self):
        suppliers = [
            "A",
            "B",
            "C"
        ]

        supplier_capacity = {
            "A": 100,
            "B": 80,
            "C": 70
        }

        limits = build_supplier_limits(
            suppliers,
            supplier_capacity
        )

        expected = [
            100,
            80,
            70
        ]

        self.assertEqual(
            limits,
            expected
        )


    def test_build_customer_requirements(self):
        customers = [
            "1",
            "2",
            "3"
        ]

        customer_demand = {
            "1": 50,
            "2": 60,
            "3": 40
        }

        requirements = (
            build_customer_requirements(
                customers,
                customer_demand
            )
        )

        expected = [
            50,
            60,
            40
        ]

        self.assertEqual(
            requirements,
            expected
        )


    def test_negative_supplier_capacity(self):
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            suffix=".csv",
            delete=False
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "supplier",
                "capacity"
            ])

            writer.writerow([
                "A",
                100
            ])

            writer.writerow([
                "B",
                -80
            ])

            filename = file.name

        try:
            with self.assertRaises(
                SystemExit
            ):
                load_suppliers(
                    filename
                )

        finally:
            os.remove(
                filename
            )


    def test_negative_customer_demand(self):
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            suffix=".csv",
            delete=False
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "customer",
                "demand"
            ])

            writer.writerow([
                "1",
                50
            ])

            writer.writerow([
                "2",
                -60
            ])

            filename = file.name

        try:
            with self.assertRaises(
                SystemExit
            ):
                load_customers(
                    filename
                )

        finally:
            os.remove(
                filename
            )


    def test_load_shipping_costs(self):
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            suffix=".csv",
            delete=False
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "supplier",
                "customer",
                "cost"
            ])

            writer.writerow([
                "A",
                "1",
                4
            ])

            writer.writerow([
                "A",
                "2",
                7
            ])

            writer.writerow([
                "B",
                "1",
                6
            ])

            writer.writerow([
                "B",
                "2",
                3
            ])

            filename = file.name

        try:
            shipping_cost = (
                load_shipping_costs(
                    filename
                )
            )

            expected = {
                ("A", "1"): 4,
                ("A", "2"): 7,
                ("B", "1"): 6,
                ("B", "2"): 3
            }

            self.assertEqual(
                shipping_cost,
                expected
            )

        finally:
            os.remove(
                filename
            )


    def test_small_optimization_model(self):
        supplier_capacity = {
            "A": 100,
            "B": 80
        }

        customer_demand = {
            "1": 50,
            "2": 60,
            "3": 40
        }

        shipping_cost = {
            ("A", "1"): 4,
            ("A", "2"): 7,
            ("A", "3"): 5,
            ("B", "1"): 6,
            ("B", "2"): 3,
            ("B", "3"): 8
        }

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

        cost_vector = (
            build_cost_vector(
                routes,
                shipping_cost
            )
        )

        A_ub = (
            build_supplier_matrix(
                suppliers,
                routes
            )
        )

        b_ub = (
            build_supplier_limits(
                suppliers,
                supplier_capacity
            )
        )

        A_eq = (
            build_customer_matrix(
                customers,
                routes
            )
        )

        b_eq = (
            build_customer_requirements(
                customers,
                customer_demand
            )
        )

        result = (
            solve_transportation_model(
                cost_vector,
                A_ub,
                b_ub,
                A_eq,
                b_eq
            )
        )

        self.assertTrue(
            result.success
        )

        self.assertAlmostEqual(
            result.fun,
            580.0,
            places=6
        )


    def test_validate_known_solution(self):
        suppliers = [
            "A",
            "B"
        ]

        customers = [
            "1",
            "2"
        ]

        supplier_capacity = {
            "A": 60,
            "B": 60
        }

        customer_demand = {
            "1": 50,
            "2": 60
        }

        routes = [
            ("A", "1"),
            ("A", "2"),
            ("B", "1"),
            ("B", "2")
        ]

        shipping_cost = {
            ("A", "1"): 4,
            ("A", "2"): 7,
            ("B", "1"): 6,
            ("B", "2"): 3
        }

        cost_vector = (
            build_cost_vector(
                routes,
                shipping_cost
            )
        )

        A_ub = (
            build_supplier_matrix(
                suppliers,
                routes
            )
        )

        b_ub = (
            build_supplier_limits(
                suppliers,
                supplier_capacity
            )
        )

        A_eq = (
            build_customer_matrix(
                customers,
                routes
            )
        )

        b_eq = (
            build_customer_requirements(
                customers,
                customer_demand
            )
        )

        result = (
            solve_transportation_model(
                cost_vector,
                A_ub,
                b_ub,
                A_eq,
                b_eq
            )
        )

        self.assertTrue(
            result.success
        )

        shipments = dict(
            zip(
                routes,
                result.x
            )
        )

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

        self.assertTrue(
            validation_passed
        )


    def test_calculate_total_cost(self):
        routes = [
            ("A", "1"),
            ("A", "2"),
            ("B", "1"),
            ("B", "2")
        ]

        shipments = {
            ("A", "1"): 50,
            ("A", "2"): 0,
            ("B", "1"): 0,
            ("B", "2"): 60
        }

        shipping_cost = {
            ("A", "1"): 4,
            ("A", "2"): 7,
            ("B", "1"): 6,
            ("B", "2"): 3
        }

        total_cost = (
            calculate_total_cost(
                routes,
                shipments,
                shipping_cost
            )
        )

        expected = 380

        self.assertEqual(
            total_cost,
            expected
        )


    # =====================================================
    # RESILIENCE TESTS
    # =====================================================

    def test_apply_supplier_disruption(self):
        supplier_capacity = {
            "A": 100,
            "B": 80
        }

        disrupted = (
            apply_supplier_disruption(
                supplier_capacity,
                "B",
                0.50
            )
        )

        self.assertEqual(
            disrupted["B"],
            40
        )


    def test_disruption_does_not_mutate_original(self):
        supplier_capacity = {
            "A": 100,
            "B": 80
        }

        apply_supplier_disruption(
            supplier_capacity,
            "B",
            0.50
        )

        self.assertEqual(
            supplier_capacity["B"],
            80
        )


    def test_solve_scenario_success(self):
        supplier_capacity = {
            "A": 100,
            "B": 80
        }

        customer_demand = {
            "1": 50,
            "2": 60
        }

        shipping_cost = {
            ("A", "1"): 4,
            ("A", "2"): 7,
            ("B", "1"): 6,
            ("B", "2"): 3
        }

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

        result = solve_scenario(
            suppliers,
            customers,
            routes,
            shipping_cost,
            supplier_capacity,
            customer_demand
        )

        self.assertTrue(
            result.success
        )


    def test_resilience_stress_test_count(self):
        supplier_capacity = {
            "A": 100,
            "B": 80
        }

        customer_demand = {
            "1": 50,
            "2": 60
        }

        shipping_cost = {
            ("A", "1"): 4,
            ("A", "2"): 7,
            ("B", "1"): 6,
            ("B", "2"): 3
        }

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

        baseline_result = (
            solve_scenario(
                suppliers,
                customers,
                routes,
                shipping_cost,
                supplier_capacity,
                customer_demand
            )
        )

        baseline_cost = (
            baseline_result.fun
        )

        stress_results = (
            run_resilience_stress_test(
                suppliers,
                customers,
                routes,
                shipping_cost,
                supplier_capacity,
                customer_demand,
                baseline_cost
            )
        )

        # 2 suppliers * 5 disruption levels
        self.assertEqual(
            len(stress_results),
            10
        )


    def test_resilience_detects_infeasible_scenario(self):
        supplier_capacity = {
            "A": 60,
            "B": 60
        }

        customer_demand = {
            "1": 50,
            "2": 60
        }

        shipping_cost = {
            ("A", "1"): 4,
            ("A", "2"): 7,
            ("B", "1"): 6,
            ("B", "2"): 3
        }

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

        baseline_result = (
            solve_scenario(
                suppliers,
                customers,
                routes,
                shipping_cost,
                supplier_capacity,
                customer_demand
            )
        )

        baseline_cost = (
            baseline_result.fun
        )

        stress_results = (
            run_resilience_stress_test(
                suppliers,
                customers,
                routes,
                shipping_cost,
                supplier_capacity,
                customer_demand,
                baseline_cost
            )
        )

        infeasible_scenarios = [
            scenario
            for scenario
            in stress_results
            if not scenario["feasible"]
        ]

        self.assertGreater(
            len(infeasible_scenarios),
            0
        )


if __name__ == "__main__":
    unittest.main()