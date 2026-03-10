import PyInstaller.__main__
import os


def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    sep = ";"  # Windows
    datas = [
        ("gdp_dashboard_streamlit.py", "."),
        ("config.json", "."),
        ("gdp_with_continent_filled.xlsx", "."),
        ("data_loader.py", "."),
        ("data_processor.py", "."),
        ("core", "core"),
        ("plugins", "plugins"),
    ]
    add_data_args = []
    for src, dst in datas:
        add_data_args.extend(["--add-data", f"{src}{sep}{dst}"])

    hidden = [
        "streamlit", "streamlit.web.cli",
        "streamlit.runtime.scriptrunner",
        "plotly", "plotly.express", "plotly.graph_objects", "plotly.subplots",
        "pycountry", "openpyxl", "numpy", "pandas",
        "data_loader", "data_processor",
        "core", "core.engine", "core.contracts",
        "plugins", "plugins.inputs", "plugins.outputs",
    ]
    hidden_args = []
    for h in hidden:
        hidden_args.extend(["--hidden-import", h])

    args = [
        "run_dashboard.py",
        "--name", "GDP_Dashboard",
        "--onedir",
        "--windowed",     # No console window -- proper desktop app
        "--noconfirm",
        *add_data_args,
        *hidden_args,
        "--collect-all", "streamlit",
        "--collect-all", "plotly",
        "--collect-all", "pycountry",
        "--copy-metadata", "streamlit",
        "--copy-metadata", "pycountry",
    ]

    print("Building GDP Dashboard desktop app...")
    PyInstaller.__main__.run(args)
    print("\nDone! -> dist/GDP_Dashboard/GDP_Dashboard.exe")


if __name__ == "__main__":
    build()

