Using **Modeleon** and **AI (Claude)** allows you to create a professional financial model that adheres strictly to **Financial Modeling Institute (FMI)** standards while keeping the entire logic layer in Python. This process ensures the resulting Excel file is dynamic, transparent, and audit-ready without manual intervention.

### 1. Architectural Setup (Python Environment)
*   **Initialization:** Setup a Python 3.12+ environment and import `modeleon` as your Domain-Specific Language (DSL). Unlike standard libraries that export static values, Modeleon emits **live Excel formulas** (e.g., `=B1*B2`), allowing the final workbook to "breathe" when assumptions change.
*   **Vertical Tab Structure:** Programmatically define the model following the FMI vertical orientation: **Cover, Summary, Assumptions, Scenarios, Model (The Engine), and Outputs**.

### 2. Grouping Factual Data (The Only Hardcodes)
To follow FMI standards, factual data must be isolated and formatted in **blue font** to distinguish them from calculation logic.
*   **Historical and Current Statements:** Use `mo.Variable()` to house historical balance sheet and income statement data. These represent the foundational facts of the business.
*   **Centralized Assumptions:** Group all operational drivers (growth rates, margins, tax rates) into a dedicated `mo.MultiVariable()` container. FMI requires these to be "up front" to provide a clear narrative of the model's drivers.
*   **Scenario Matrices:** Define three core cases—**Base, Best, and Worst**—for key drivers. Modeleon allows you to define these as Python dictionaries that translate into a centralized scenario table in Excel.

### 3. Building the Calculation Engine (No Hardcoding)
The FMI's most critical rule is that **formulas must never contain hardcoded numbers** (e.g., no `* 1.05`). 
*   **Variable References:** Define formulas in Python using object references. Modeleon automatically generates Excel cell references (e.g., `revenue = units * price`).
*   **Time-Series Projections:** Use `mo.recurrence()` to build time-series logic for the **10 Essential Schedules** (Revenue, Operating Costs, PP&E, Tax, Working Capital, etc.). For example: `debt_balance = mo.recurrence(opening, "{prev} - {repayment}")`.
*   **Single Entry Rule:** Modeleon enforces the FMI rule to **never enter the same variable twice**. You define a variable once in Python, and every subsequent use in the schedules or financial statements links back to that single object.

### 4. Vertical Stacking and Hierarchical Linkage
*   **Sequential Stacking:** Organize the Python objects so they compile into a single "Model" tab where schedules are stacked vertically above the three integrated financial statements.
*   **Column Alignment:** Ensure every period column is perfectly aligned across all stacked tables (e.g., Column G always represents the first forecast year). 
*   **Formula Flow:** Link calculation results from the schedules into the **Income Statement, Cash Flow Statement, and Balance Sheet**. The financial statements themselves should contain only simple links, never nested calculations.

### 5. Dynamic Scenario and Error Logic
*   **The Scenario Switch:** Implement a single `Scenario_ID` variable. Use the `mo.CHOOSE()` or `mo.INDEX()` function to retrieve the active case assumptions for the schedules.
*   **Audit Checks:** Programmatically include a **Master Check Section** at the top of the model. This should include an automated **Balance Sheet Check** (`Assets - Liabilities - Equity = 0`) that displays "OK" or "ERROR" using conditional formatting.
*   **Circularity Management:** For complex logic like a debt revolver, use Python to wrap circular interest calculations in a logical breaker to maintain model stability.

### 6. Automated Formatting and Print Export
Modeleon allows you to set professional visual standards via code so the model is "presentation-ready" the moment it is opened:
*   **FMI Color-Coding:** Code Modeleon to apply **Blue** for inputs, **Black** for internal formulas, and **Green** for cross-sheet references.
*   **Print Configuration:** Set the workbook to **Landscape orientation**, scaling between **85% and 95%**, and margins between **0.25" and 0.4"**.
*   **Metadata Headers:** Programmatically insert headers and footers containing the **File Path, Filename, Page Numbers ("Page X of Y"), and a Date/Time Stamp**.
*   **Final Output:** Compile the script to a `.xlsx` file. You can then open it solely to **print to PDF**, ensuring a high-caliber professional delivery without manual Excel tweaking.