import typing
import sqlite3

from rich import box
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.layout import Layout
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC


CONSOLE: typing.Final[Console] = Console()
CONNECTION: typing.Final[sqlite3.Connection] = sqlite3.connect("EE08.sqlite")
CURSOR: typing.Final[sqlite3.Cursor] = CONNECTION.cursor()


class ComponentDesigner:
    @staticmethod
    def create_browser_selection_table() -> Table:
        table = Table(
            title="🌐 Select Your Preferred Browser 🌐",
            title_style="bold magenta",
            border_style="bright_blue",
            box=box.ROUNDED,
            safe_box=False,
            expand=True
        )
        table.add_column(Align.center("Browser ID"), style="cyan bold", justify="center")
        table.add_column(Align.center("Browser Name"), style="bold")
        table.add_row(Align.center("1️⃣"), Align.center("🧩 Google Chrome 🧩"))
        table.add_row(Align.center("2️⃣"), Align.center("🦅 Microsoft Edge 🦅"))
        table.add_row(Align.center("3️⃣"), Align.center("🦊 Mozilla Firefox 🦊"))
        table.add_row(Align.center("4️⃣"), Align.center("🧭 Safari 🧭"))
        return table

    @staticmethod
    def create_driver_not_found_panel() -> Panel:
        return Panel(Align.center("[b]😥 Driver for this browser is not found on your PC 😥"), border_style="red")

    @staticmethod
    def create_selected_browser_panel(browser_name: str) -> Panel:
        return Panel(Align.center(browser_name, vertical="middle"), title="[b]Selected Browser", border_style="white")

    @staticmethod
    def create_progress_tracker() -> Progress:
        return Progress(BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"))

    @staticmethod
    def create_question_solving_progress_panel(progress_tracker: Progress) -> Panel:
        return Panel(
            Align.center(progress_tracker, vertical="middle"),
            border_style="red",
            title="[b]Question Solving Progress"
        )


class DriverFactory:
    @staticmethod
    def create_driver_from(browser_id: int) -> WebDriver | None:
        try:
            match browser_id:
                case 1:
                    options = webdriver.ChromeOptions()
                    options.add_experimental_option("excludeSwitches", ["enable-logging"])
                    driver = webdriver.Chrome(options=options)
                case 2:
                    options = webdriver.EdgeOptions()
                    options.add_experimental_option("excludeSwitches", ["enable-logging"])
                    driver = webdriver.Edge(options=options)
                case 3:
                    options = webdriver.FirefoxOptions()
                    options.set_preference("devtools.console.stdout.content", False)
                    driver = webdriver.Firefox(options=options)
                case 4:
                    service = webdriver.SafariService(enable_logging=False)
                    driver = webdriver.Safari(service=service)
        except:
            return None
        else:
            driver.minimize_window()
            return driver


def main() -> None:
    CONSOLE.print(ComponentDesigner.create_browser_selection_table(), new_line_start=True)

    print() # Newline

    browser_id = int(Prompt.ask("[bold cyan]Enter the ID of the browser", choices=["1", "2", "3", "4"], show_choices=False))

    print() # Newline

    driver = DriverFactory.create_driver_from(browser_id)

    if driver is None:
        return CONSOLE.print(ComponentDesigner.create_driver_not_found_panel())

    CONSOLE.clear()

    driver.get("https://egzamin-informatyk.pl/testy-inf02-ee08-sprzet-systemy-sieci/")

    try:
        reject_cookies_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "fc-secondary-button"))
        )
    except:
        pass
    else:
        reject_cookies_button.click()

    root_layout = Layout()

    match browser_id:
        case 1:
            browser_name = "🧩 Google Chrome 🧩"
        case 2:
            browser_name = "🦅 Microsoft Edge 🦅"
        case 3:
            browser_name = "🦊 Mozilla Firefox 🦊"
        case 4:
            browser_name = "🧭 Safari 🧭"

    chosen_browser_panel = ComponentDesigner.create_selected_browser_panel(browser_name)

    question_solving_progress = ComponentDesigner.create_progress_tracker()

    question_solving_progress.add_task("Solving Questions", total=40)

    question_solving_panel = ComponentDesigner.create_question_solving_progress_panel(question_solving_progress)

    root_layout.split_column(chosen_browser_panel, question_solving_panel)

    with Live(root_layout, refresh_per_second=10, screen=False):
        for i, ee08_question_box in enumerate(driver.find_elements(By.CLASS_NAME, "trescE"), 1):
            if i < 10:
                ee08_question = ee08_question_box.text[3:]
            else:
                ee08_question = ee08_question_box.text[4:]

            answer_divs = [
                driver.find_element(By.ID, f"odpa{i}"),
                driver.find_element(By.ID, f"odpb{i}"),
                driver.find_element(By.ID, f"odpc{i}"),
                driver.find_element(By.ID, f"odpd{i}"),
            ]

            CURSOR.execute("SELECT answer FROM EE08 WHERE question=?", (ee08_question,))
            rows = CURSOR.fetchall()

            for row in rows:
                for answer_div in answer_divs:
                    if answer_div.text[3:] == row[0]:
                        answer_div_id = answer_div.get_attribute("id")

                        assert answer_div_id is not None

                        driver.execute_script(
                            "document.getElementById(arguments[0]).checked = true;",
                            f"ans{answer_div_id[3]}{i}"
                        )

            question_solving_progress.advance(question_solving_progress.tasks[0].id)

    print() # Newline

    Prompt.ask("[bold cyan] Press Enter to close the browser...")

    driver.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass