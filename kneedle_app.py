import sys
import io
import numpy as np
import pandas as pd
from math import sqrt

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFileDialog, QMessageBox

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from scipy.interpolate import UnivariateSpline
from scipy.signal import find_peaks


# Prosty system tekstów PL/EN
TEXT = {
    "PL": {
        "title": "Kneedle — analiza liczebności próby",
        "btn_load": "Import CSV / Excel",
        "btn_paste": "Wklej dane (kolumna obserwacji lub n,f(n))",
        "n_from": "n od:",
        "n_to": "do:",
        "step": "krok:",
        "S": "S (czułość):",
        "use_online": "Użyj logiki online (próg i spadek)",
        "run": "Uruchom Kneedle",
        "save_csv": "Zapisz wyniki CSV",
        "save_plots": "Zapisz wykresy (PNG)",
        "lang_btn": "PL / EN",
        "file_dialog": "Wybierz plik CSV lub Excel",
        "file_filter": "CSV (*.csv);;Excel (*.xlsx *.xls)",
        "err_load": "Nie można wczytać pliku:\n{}",
        "no_data": "Brak danych. Importuj plik lub wklej dane.",
        "clipboard_empty": "Schowek jest pusty.",
        "clipboard_title": "Brak danych",
        "clipboard_err": "Nie można sparsować wklejonych danych: {}",
        "pasted_cols": "Wklejono dane — kolumny: {}",
        "loaded_cols": "Wczytano plik: {} — kolumny: {}",
        "sigma_msg": "Obliczono sigma={:.6g} z {} obserwacji; wygenerowano f(n)=sigma/sqrt(n).",
        "format_err": "Nie rozpoznano formatu danych. Wklej kolumnę obserwacji lub pary n,f(n).",
        "knee_offline": "Knee (offline, max diff) przy n={}",
        "knee_online_none": "Knee (online) nie wykryto dla bieżącego S i danych.",
        "knee_online_many": "Knee (online) wykryte przy n={}",
        "no_results": "Uruchom analizę, aby zapisać wyniki.",
        "no_results_title": "Brak wyników",
        "save_csv_dialog": "Zapisz wyniki jako CSV",
        "save_csv_name": "kneedle_results.csv",
        "save_csv_filter": "CSV (*.csv)",
        "save_csv_ok": "Wyniki zapisane do: {}",
        "save_csv_err": "Błąd zapisu",
        "save_plots_dialog": "Zapisz wykresy (zapisze 3 pliki PNG z sufiksami)",
        "save_plots_name": "kneedle_plot",
        "save_plots_filter": "PNG (*.png)",
        "save_plots_ok": "Wykresy zapisane jako: {}_*.png",
        "save_plots_err": "Błąd zapisu wykresów",
        "monot_warn": "Uwaga: f(n) nie jest monotonicznie malejące — wyniki Kneedle mogą być niestabilne.",
        "const_warn": "Uwaga: dane są stałe — normalizacja zdegenerowana.",
        "error_title": "Błąd",
        "plot1_title": "Znormalizowana krzywa i linia odniesienia",
        "plot1_xlabel": "x_sn",
        "plot1_ylabel": "y_sn",
        "plot1_l1": "y_sn (znormalizowana)",
        "plot1_l2": "y = x",
        "plot2_title": "Krzywa różnicowa y_sn - x_sn",
        "plot2_xlabel": "x_sn",
        "plot2_ylabel": "y_sn - x_sn",
        "plot2_l1": "y_sn - x_sn",
        "plot2_l2": "lokalne maksima",
        "plot2_l3": "aktywny próg",
        "plot3_title": "Oryginalna skala f(n) vs n",
        "plot3_xlabel": "n",
        "plot3_ylabel": "f(n)",
        "plot3_l1": "f(n) surowe",
        "plot3_l2": "f(n) wygładzone",
    },
    "EN": {
        "title": "Kneedle — sample size analysis",
        "btn_load": "Import CSV / Excel",
        "btn_paste": "Paste data (single column or n,f(n))",
        "n_from": "n from:",
        "n_to": "to:",
        "step": "step:",
        "S": "S (sensitivity):",
        "use_online": "Use online logic (threshold & drop)",
        "run": "Run Kneedle",
        "save_csv": "Save results CSV",
        "save_plots": "Save plots (PNG)",
        "lang_btn": "PL / EN",
        "file_dialog": "Select CSV or Excel file",
        "file_filter": "CSV (*.csv);;Excel (*.xlsx *.xls)",
        "err_load": "Cannot read file:\n{}",
        "no_data": "No data. Import a file or paste data.",
        "clipboard_empty": "Clipboard is empty.",
        "clipboard_title": "No data",
        "clipboard_err": "Cannot parse pasted data: {}",
        "pasted_cols": "Pasted data — columns: {}",
        "loaded_cols": "Loaded file: {} — columns: {}",
        "sigma_msg": "Computed sigma={:.6g} from {} observations; generated f(n)=sigma/sqrt(n).",
        "format_err": "Unrecognized data format. Paste a column of observations or pairs n,f(n).",
        "knee_offline": "Knee (offline, max diff) at n={}",
        "knee_online_none": "Knee (online) not detected for current S and data.",
        "knee_online_many": "Knee (online) detected at n={}",
        "no_results": "Run analysis before saving results.",
        "no_results_title": "No results",
        "save_csv_dialog": "Save results as CSV",
        "save_csv_name": "kneedle_results.csv",
        "save_csv_filter": "CSV (*.csv)",
        "save_csv_ok": "Results saved to: {}",
        "save_csv_err": "Save error",
        "save_plots_dialog": "Save plots (will save 3 PNG files with suffixes)",
        "save_plots_name": "kneedle_plot",
        "save_plots_filter": "PNG (*.png)",
        "save_plots_ok": "Plots saved as: {}_*.png",
        "save_plots_err": "Plot save error",
        "monot_warn": "Warning: f(n) is not monotonically decreasing — Kneedle results may be unstable.",
        "const_warn": "Warning: data are constant — normalization is degenerate.",
        "error_title": "Error",
        "plot1_title": "Normalized curve and reference line",
        "plot1_xlabel": "x_sn",
        "plot1_ylabel": "y_sn",
        "plot1_l1": "y_sn (normalized)",
        "plot1_l2": "y = x",
        "plot2_title": "Difference curve y_sn - x_sn",
        "plot2_xlabel": "x_sn",
        "plot2_ylabel": "y_sn - x_sn",
        "plot2_l1": "y_sn - x_sn",
        "plot2_l2": "local maxima",
        "plot2_l3": "active threshold",
        "plot3_title": "Original scale f(n) vs n",
        "plot3_xlabel": "n",
        "plot3_ylabel": "f(n)",
        "plot3_l1": "f(n) raw",
        "plot3_l2": "f(n) smooth",
    }
}

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        super().__init__(fig)
        self.axes = fig.subplots(1, 1)


class KneedleApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "PL"
        self.df = None
        self.results = None
        self._build_ui()
        self._apply_language()

    # ---------- UI ----------

    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        controls = QtWidgets.QHBoxLayout()
        layout.addLayout(controls)

        self.btn_load = QtWidgets.QPushButton()
        self.btn_load.clicked.connect(self.load_file)
        controls.addWidget(self.btn_load)

        self.btn_paste = QtWidgets.QPushButton()
        self.btn_paste.clicked.connect(self.paste_data)
        controls.addWidget(self.btn_paste)

        controls.addSpacing(10)
        self.lbl_n_from = QtWidgets.QLabel()
        controls.addWidget(self.lbl_n_from)
        self.spin_n_from = QtWidgets.QSpinBox()
        self.spin_n_from.setRange(1, 1000000)
        self.spin_n_from.setValue(10)
        controls.addWidget(self.spin_n_from)

        self.lbl_n_to = QtWidgets.QLabel()
        controls.addWidget(self.lbl_n_to)
        self.spin_n_to = QtWidgets.QSpinBox()
        self.spin_n_to.setRange(1, 1000000)
        self.spin_n_to.setValue(2000)
        controls.addWidget(self.spin_n_to)

        self.lbl_step = QtWidgets.QLabel()
        controls.addWidget(self.lbl_step)
        self.spin_step = QtWidgets.QSpinBox()
        self.spin_step.setRange(1, 1000000)
        self.spin_step.setValue(10)
        controls.addWidget(self.spin_step)

        controls.addSpacing(10)
        self.lbl_S = QtWidgets.QLabel()
        controls.addWidget(self.lbl_S)
        self.edit_S = QtWidgets.QDoubleSpinBox()
        self.edit_S.setRange(0.0, 100.0)
        self.edit_S.setValue(1.0)
        self.edit_S.setSingleStep(0.1)
        controls.addWidget(self.edit_S)

        controls.addSpacing(10)
        self.chk_use_online = QtWidgets.QCheckBox()
        self.chk_use_online.setChecked(True)
        controls.addWidget(self.chk_use_online)

        self.btn_run = QtWidgets.QPushButton()
        self.btn_run.clicked.connect(self.run_kneedle)
        controls.addWidget(self.btn_run)

        self.btn_lang = QtWidgets.QPushButton()
        self.btn_lang.clicked.connect(self.toggle_language)
        controls.addWidget(self.btn_lang)

        plots_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(plots_layout)

        self.canvas1 = MplCanvas(self, width=5, height=4)
        self.canvas2 = MplCanvas(self, width=5, height=4)
        self.canvas3 = MplCanvas(self, width=5, height=4)

        plots_layout.addWidget(self.canvas1)
        plots_layout.addWidget(self.canvas2)
        plots_layout.addWidget(self.canvas3)

        bottom = QtWidgets.QHBoxLayout()
        layout.addLayout(bottom)

        self.txt_log = QtWidgets.QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(140)
        bottom.addWidget(self.txt_log)

        right_buttons = QtWidgets.QVBoxLayout()
        bottom.addLayout(right_buttons)

        self.btn_save_csv = QtWidgets.QPushButton()
        self.btn_save_csv.clicked.connect(self.save_csv)
        right_buttons.addWidget(self.btn_save_csv)

        self.btn_save_plots = QtWidgets.QPushButton()
        self.btn_save_plots.clicked.connect(self.save_plots)
        right_buttons.addWidget(self.btn_save_plots)

        right_buttons.addStretch()

    def _apply_language(self):
        t = TEXT[self.lang]
        self.setWindowTitle(t["title"])
        self.btn_load.setText(t["btn_load"])
        self.btn_paste.setText(t["btn_paste"])
        self.lbl_n_from.setText(t["n_from"])
        self.lbl_n_to.setText(t["n_to"])
        self.lbl_step.setText(t["step"])
        self.lbl_S.setText(t["S"])
        self.chk_use_online.setText(t["use_online"])
        self.btn_run.setText(t["run"])
        self.btn_lang.setText(t["lang_btn"])
        self.btn_save_csv.setText(t["save_csv"])
        self.btn_save_plots.setText(t["save_plots"])

    def toggle_language(self):
        self.lang = "EN" if self.lang == "PL" else "PL"
        self._apply_language()

    def log(self, key, *args):
        msg = TEXT[self.lang][key].format(*args)
        self.txt_log.append(msg)

    # ---------- Dane ----------

    def load_file(self):
        t = TEXT[self.lang]
        path, _ = QFileDialog.getOpenFileName(
            self, t["file_dialog"], "", t["file_filter"]
        )
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
        except Exception as e:
            QMessageBox.critical(self, t["error_title"], t["err_load"].format(e))
            return
        self.df = df
        cols = ", ".join(df.columns.astype(str))
        self.log("loaded_cols", path, cols)

    def paste_data(self):
        t = TEXT[self.lang]
        text = QtWidgets.QApplication.clipboard().text()
        if not text.strip():
            QMessageBox.information(self, t["clipboard_title"], t["clipboard_empty"])
            return
        try:
            df = pd.read_csv(io.StringIO(text), sep=None, engine="python")
        except Exception:
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            try:
                vals = [float(l.replace(",", ".")) for l in lines]
                df = pd.DataFrame({"obs": vals})
            except Exception as e:
                QMessageBox.critical(self, t["error_title"], t["clipboard_err"].format(e))
                return
        self.df = df
        cols = ", ".join(df.columns.astype(str))
        self.log("pasted_cols", cols)

    def prepare_curve(self):
        """
        Przygotowuje wektor n i f(n) na podstawie self.df i ustawień GUI.
        Zwraca (n_array, f_array, mode) gdzie mode in {'observations','curve'}.
        """
        t = TEXT[self.lang]
        if self.df is None:
            raise ValueError(t["no_data"])
        df = self.df.copy()
        cols_lower = [c.lower() for c in df.columns.astype(str)]

        # 1) jawne n, f(n)
        if ("n" in cols_lower and
            any(c in cols_lower for c in ("f", "f(n)", "cost", "error", "błąd", "blad"))):
            col_n = df.columns[[c.lower() == "n" for c in cols_lower]][0]
            f_candidates = [
                i for i, c in enumerate(cols_lower)
                if c in ("f", "f(n)", "cost", "error", "błąd", "blad")
            ]
            if not f_candidates:
                f_candidates = [i for i, c in enumerate(cols_lower) if c != "n"]
            col_f = df.columns[f_candidates[0]]
            n = df[col_n].astype(float).values
            f = df[col_f].astype(float).values
            return n, f, "curve"

        # 2) dwie kolumny -> n, f
        if df.shape[1] == 2:
            n = df.iloc[:, 0].astype(float).values
            f = df.iloc[:, 1].astype(float).values
            return n, f, "curve"

        # 3) jedna kolumna -> obserwacje
        if df.shape[1] == 1:
            vals = df.iloc[:, 0].astype(float).values
            sigma = np.std(vals, ddof=1)
            n_from = self.spin_n_from.value()
            n_to = self.spin_n_to.value()
            step = self.spin_step.value()
            n = np.arange(n_from, n_to + 1, step, dtype=float)
            f = sigma / np.sqrt(n)
            self.log("sigma_msg", sigma, len(vals))
            return n, f, "observations"

        # 4) fallback: pierwsza numeryczna kolumna jako f(n), n z zakresu
        fcol = None
        for c in df.columns:
            try:
                arr = df[c].astype(float).values
                fcol = arr
                break
            except Exception:
                continue
        if fcol is not None:
            n_from = self.spin_n_from.value()
            n_to = self.spin_n_to.value()
            step = self.spin_step.value()
            n = np.arange(n_from, n_to + 1, step, dtype=float)
            if len(fcol) == len(n):
                return n, fcol, "curve"
            f_interp = np.interp(n, np.linspace(n_from, n_to, len(fcol)), fcol)
            return n, f_interp, "curve"

        raise ValueError(t["format_err"])

    # ---------- Kneedle ----------

    def smooth_curve(self, n, f):
        """
        Wygładzanie krzywej f(n) za pomocą UnivariateSpline (SciPy).
        """
        # zabezpieczenie: potrzebujemy co najmniej kilku punktów
        if len(n) < 5:
            return f.copy()
        # sortowanie po n (na wszelki wypadek)
        order = np.argsort(n)
        n_sorted = n[order]
        f_sorted = f[order]
        # parametr s: lekki smoothing, skalowany liczbą punktów
        s = len(n_sorted) * 0.001
        try:
            spline = UnivariateSpline(n_sorted, f_sorted, s=s)
            f_smooth = spline(n_sorted)
            # przywróć oryginalną kolejność
            inv = np.argsort(order)
            return f_smooth[inv]
        except Exception:
            # w razie problemów wracamy do oryginalnych danych
            return f.copy()

    def run_kneedle(self):
        t = TEXT[self.lang]
        try:
            n, f_raw, mode = self.prepare_curve()
        except Exception as e:
            QMessageBox.critical(self, t["error_title"], str(e))
            return

        # ostrzeżenie o niemonotoniczności
        if not np.all(np.diff(f_raw) <= 1e-12):
            self.txt_log.append(t["monot_warn"])

        # smoothing spline
        f = self.smooth_curve(n, f_raw)

        # normalizacja
        if n.max() == n.min() or f.max() == f.min():
            self.txt_log.append(t["const_warn"])
        xsn = (n - n.min()) / (n.max() - n.min()) if n.max() != n.min() else np.zeros_like(n)
        ysn = (np.max(f) - f) / (np.max(f) - np.min(f)) if np.max(f) != np.min(f) else np.zeros_like(f)
        diff = ysn - xsn

        # lokalne maksima (na krzywej różnic)
        # używamy scipy.signal.find_peaks
        peaks, _ = find_peaks(diff)
        local_max = np.full_like(diff, np.nan)
        local_max[peaks] = diff[peaks]

        # średni krok w osi X
        dxs = np.diff(xsn)
        mean_dx = np.mean(dxs) if len(dxs) > 0 else 0.0
        S = float(self.edit_S.value())

        # próg dla każdego lokalnego maksimum
        threshold = np.full_like(diff, np.nan)
        for i in peaks:
            threshold[i] = local_max[i] - S * mean_dx

        # aktywny próg (online-style)
        active_threshold = np.full_like(diff, np.nan)
        current = np.nan
        for i in range(len(diff)):
            if not np.isnan(threshold[i]):
                current = threshold[i]
            active_threshold[i] = current

        # detekcja knees online: dla każdego lokalnego maksimum
        knees_online_idx = []
        if self.chk_use_online.isChecked() and len(peaks) > 0:
            for p in peaks:
                thr = threshold[p]
                if np.isnan(thr):
                    continue
                # szukamy pierwszego spadku poniżej progu po p
                for j in range(p + 1, len(diff)):
                    if diff[j] < thr:
                        knees_online_idx.append(p)
                        break
        knees_online_idx = sorted(set(knees_online_idx))

        # offline knees: globalne maksimum + inne silne maksima
        if len(diff) > 0:
            knee_offline_main = int(np.nanargmax(diff))
        else:
            knee_offline_main = None

        # dodatkowe offline knees: inne piki powyżej np. 90% max diff
        knees_offline_idx = []
        if len(peaks) > 0:
            max_diff = np.nanmax(diff)
            for p in peaks:
                if diff[p] >= 0.9 * max_diff:
                    knees_offline_idx.append(int(p))
        if knee_offline_main is not None and knee_offline_main not in knees_offline_idx:
            knees_offline_idx.append(knee_offline_main)
        knees_offline_idx = sorted(set(knees_offline_idx))

        # tabela wyników
        res_df = pd.DataFrame({
            "n": n,
            "f_raw": f_raw,
            "f_smooth": f,
            "xsn": xsn,
            "ysn": ysn,
            "y_minus_x": diff,
            "local_max": local_max,
            "threshold": threshold,
            "active_threshold": active_threshold,
        })
        res_df["knee_offline"] = False
        res_df["knee_online"] = False
        for idx in knees_offline_idx:
            res_df.loc[idx, "knee_offline"] = True
        for idx in knees_online_idx:
            res_df.loc[idx, "knee_online"] = True

        self.results = res_df

        # logi
        if knees_offline_idx:
            ns = [int(n[i]) for i in knees_offline_idx]
            self.log("knee_offline", ns)
        if knees_online_idx:
            ns_on = [int(n[i]) for i in knees_online_idx]
            self.log("knee_online_many", ns_on)
        else:
            self.txt_log.append(t["knee_online_none"])

        # rysowanie
        self.plot_all(
            n, f_raw, f, xsn, ysn, diff,
            local_max, threshold, active_threshold,
            knees_offline_idx, knees_online_idx
        )

    # ---------- Wykresy ----------

    def plot_all(self, n, f_raw, f_smooth, xsn, ysn, diff,
                 local_max, threshold, active_threshold,
                 knees_off, knees_on):
        t = TEXT[self.lang]

        ax = self.canvas1.axes
        ax.clear()
        ax.plot(xsn, ysn, "-o", label=t["plot1_l1"], markersize=4)
        ax.plot(xsn, xsn, "--", color="gray", label=t["plot1_l2"])
        for idx in knees_off:
            ax.axvline(x=xsn[idx], color="red", linestyle=":", alpha=0.7)
        ax.set_title(t["plot1_title"])
        ax.set_xlabel(t["plot1_xlabel"])
        ax.set_ylabel(t["plot1_ylabel"])
        ax.legend()
        self.canvas1.draw()

        ax2 = self.canvas2.axes
        ax2.clear()
        ax2.plot(xsn, diff, "-o", label=t["plot2_l1"], markersize=4)
        lm_x = xsn[~np.isnan(local_max)]
        lm_y = local_max[~np.isnan(local_max)]
        if len(lm_x) > 0:
            ax2.scatter(lm_x, lm_y, color="orange", s=60, zorder=5, label=t["plot2_l2"])
        if not np.all(np.isnan(active_threshold)):
            ax2.plot(xsn, active_threshold, color="green", linestyle="--", label=t["plot2_l3"])
        for idx in knees_on:
            ax2.axvline(x=xsn[idx], color="magenta", linestyle=":", alpha=0.7)
        ax2.set_title(t["plot2_title"])
        ax2.set_xlabel(t["plot2_xlabel"])
        ax2.set_ylabel(t["plot2_ylabel"])
        ax2.legend()
        self.canvas2.draw()

        ax3 = self.canvas3.axes
        ax3.clear()
        ax3.plot(n, f_raw, "-o", label=t["plot3_l1"], markersize=4, alpha=0.5)
        ax3.plot(n, f_smooth, "-s", label=t["plot3_l2"], markersize=3)
        for idx in knees_off:
            ax3.axvline(x=n[idx], color="red", linestyle=":", alpha=0.7)
        for idx in knees_on:
            ax3.axvline(x=n[idx], color="magenta", linestyle="--", alpha=0.7)
        ax3.set_title(t["plot3_title"])
        ax3.set_xlabel(t["plot3_xlabel"])
        ax3.set_ylabel(t["plot3_ylabel"])
        ax3.legend()
        self.canvas3.draw()

    # ---------- Zapis ----------

    def save_csv(self):
        t = TEXT[self.lang]
        if self.results is None:
            QMessageBox.information(self, t["no_results_title"], t["no_results"])
            return
        path, _ = QFileDialog.getSaveFileName(
            self, t["save_csv_dialog"], t["save_csv_name"], t["save_csv_filter"]
        )
        if not path:
            return
        try:
            self.results.to_csv(path, index=False)
            self.log("save_csv_ok", path)
        except Exception as e:
            QMessageBox.critical(self, t["save_csv_err"], str(e))

    def save_plots(self):
        t = TEXT[self.lang]
        path, _ = QFileDialog.getSaveFileName(
            self, t["save_plots_dialog"], t["save_plots_name"], t["save_plots_filter"]
        )
        if not path:
            return
        base = path.rsplit(".", 1)[0]
        try:
            self.canvas1.figure.savefig(base + "_normalized.png")
            self.canvas2.figure.savefig(base + "_diff.png")
            self.canvas3.figure.savefig(base + "_original.png")
            self.log("save_plots_ok", base)
        except Exception as e:
            QMessageBox.critical(self, t["save_plots_err"], str(e))


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = KneedleApp()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
