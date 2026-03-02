# Kneedle App: Detection of Knee Points in System Behavior

A Python-based desktop application implementing the Kneedle algorithm with a graphical user interface (PySide6). This tool provides both offline and online knee detection capabilities, making it applicable to a wide range of systems.

## Theoretical Background

In system analysis, "knees" typically represent beneficial points that system designers have long selected to best balance inherent trade-offs. The problem of finding a "good" operating point is common across widely disparate areas, from MapReduce task execution to congestion-responsive network protocols. 

The Kneedle algorithm defines a knee for continuous functions using the mathematical concept of curvature. For any continuous function $f$, there exists a standard closed-form $K_{f}(x)$ that defines the curvature of $f$ at any point:

$$K_{f}(x)=\frac{f^{\prime\prime}(x)}{(1+f^{\prime}(x)^{2})^{1.5}}$$

Maximum curvature captures the leveling off effect operators use to identify knees. Because curvature cannot be directly computed for discrete and potentially noisy data sets, the Kneedle algorithm approximates this by mapping the data to a unit square and computing the local maxima of the difference curve between the normalized data points and a reference straight line.

## Features and Algorithm Implementation

Our implementation strictly follows the methodology proposed by Satopää et al.:

1. **Data Smoothing:** The tool utilizes a smoothing spline (`scipy.interpolate.UnivariateSpline`) to preserve the shape of the original data set while mitigating noise.
2. **Normalization:** Data is normalized to the unit square to ensure the algorithm functions regardless of the magnitude of the underlying values.
3. **Difference Curve:** The algorithm calculates the set of differences between the $x$- and $y$-values to identify when the curve changes from horizontal to sharply decreasing.
4. **Offline Detection:** Detects the global maximum difference, alongside other strong local maxima.
5. **Online Detection:** Evaluates real-time threshold drops based on a user-defined sensitivity parameter $S$. Smaller values for $S$ detect knees quicker, while larger values are more conservative.

## Installation

1. Clone this repository:
   ```bash
   git clone [https://github.com/WorthySubset151/kneedle-app.git](https://github.com/WorthySubset151/kneedle-app.git)
   cd kneedle-app
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script from your terminal:

```bash
python kneedle_app.py
```

1. **Load Data:** Import a `.csv`/`.xlsx` file or paste a single column of observations or $n, f(n)$ pairs directly from the clipboard.
2. **Configure Parameters:** Set your sensitivity ($S$) and the specific data range.
3. **Run Kneedle:** Execute the analysis. The application generates three analytical plots:
    * Normalized curve and reference line $y=x$.
    * Difference curve $y_{sn} - x_{sn}$.
    * Original scale $f(n)$ vs $n$.
4. **Save Results:** Export the numerical results to a CSV file and the generated matplotlib plots to PNG files for publication.

## Reference

If you use this software in your research, please cite the original mathematical formulation of the Kneedle algorithm:

> Ville Satopää, Jeannie Albrecht, David Irwin, and Barath Raghavan. "Finding a 'Kneedle' in a Haystack: Detecting Knee Points in System Behavior." 2011. DOI: https://doi.org/10.1109/ICDCSW.2011.20