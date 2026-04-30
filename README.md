# Constraint-Based-Modeling-of-EBPR-Metabolism-in-Candidatus-Accumulibacter-phosphatis
This project models EBPR metabolism using FBA to understand phosphate release and uptake under anaerobic and aerobic conditions. It explores how metabolic constraints and environmental factors drive phosphorus cycling in wastewater systems.

## 📌 Overview
This project focuses on understanding the metabolic mechanisms underlying Enhanced Biological Phosphorus Removal (EBPR) using a constraint-based modeling approach. A simplified stoichiometric model of *Candidatus Accumulibacter phosphatis* metabolism was constructed and analyzed using Flux Balance Analysis (FBA) to simulate anaerobic and aerobic phases of wastewater treatment systems.

---

## 🎯 Research Objective
To investigate how metabolic constraints and environmental conditions regulate phosphate release and uptake in EBPR systems, and to understand how these behaviors emerge from intracellular metabolic networks.

---

## ❓ Core Research Question
What metabolic and environmental conditions promote phosphate release versus phosphate uptake in *Accumulibacter*, and how are these behaviors governed by stoichiometric and energetic constraints?

---

## ⚙️ Methodology

### 🧬 Model Construction
A simplified stoichiometric model was developed including:

- **Core Storage Metabolism**
  - Acetate activation (AC_ACT)
  - PHA synthesis/degradation (PHA_SYN, PHA_DEG)
  - Polyphosphate metabolism (PP_SYN, PP_DEG)
  - Glycogen degradation (GLY_DEG)

- **Central Carbon Metabolism**
  - Glycolysis
  - TCA Cycle
  - Respiration

- **Energy System**
  - ATP maintenance reaction (ATPM)

- **Exchange Reactions**
  - Acetate (EX_ac_e)
  - Oxygen (EX_o2_e)
  - Phosphate (EX_pi_e)

---

### 🔬 Modeling Framework
- COBRApy-based implementation  
- Steady-state assumption:  
  **S · v = 0**
- Linear programming for optimization  
- Phase-specific objective functions  

---

## 🔁 Simulation Strategy

### 🟥 Anaerobic Phase
- Oxygen uptake = 0  
- Acetate available  
- Objective: Maximize PHA synthesis  

**Observed:**
- High PHA accumulation  
- Active polyphosphate degradation  
- Phosphate released  

👉 *Energy is generated from polyphosphate breakdown*

---

### 🟩 Aerobic Phase
- Oxygen available  
- Acetate uptake blocked  
- Objective: Maximize polyphosphate synthesis  

**Observed:**
- PHA degradation  
- Active respiration  
- Phosphate uptake  

👉 *ATP from respiration drives phosphate storage*

---

## 📊 Key Results

- Phosphate cycling is an **emergent property of metabolic constraints**
- Anaerobic phase:
  - Carbon uptake drives PHA accumulation
  - Polyphosphate degradation supplies ATP
- Aerobic phase:
  - Stored carbon fuels respiration
  - ATP drives phosphate uptake
- Oxygen availability directly controls aerobic efficiency
- Carbon availability limits anaerobic storage metabolism

---

## 🔍 Sensitivity Analysis

The model was tested under varying conditions:

- **Acetate availability**
  → Controls PHA synthesis capacity  

- **Oxygen limitation**
  → Reduces respiration and phosphate uptake  

- **Polyphosphate availability**
  → Essential for ATP generation in anaerobic phase  

- **Glycogen pool**
  → Minimal effect under tested conditions  

- **ATP maintenance demand**
  → Influences overall metabolic balance  

---

## 📈 Key Insights

- Metabolic behavior is governed by **stoichiometric constraints**, not isolated reactions  
- Objective function determines phase-specific metabolic outcomes  
- Carbon–energy–redox coupling drives phosphate cycling  
- EBPR efficiency depends on environmental control (oxygen, carbon input)

---

## 🏭 Industrial Relevance

This model provides insights into:

- Optimizing aeration strategies  
- Designing carbon dosing protocols  
- Predicting phosphate removal efficiency  
- Understanding system failure under stress conditions  

---

## 🔧 Tools and Technologies

- COBRApy  
- Python (NumPy, SciPy, Pandas)  
- Linear Programming (FBA)  

---

## 🚀 Future Work

- Incorporate dynamic FBA (time-dependent modeling)  
- Add multiple carbon sources (propionate, glucose)  
- Introduce oxygen gradients  
- Include regulatory constraints (gene expression)  
- Expand model to include denitrification pathways  
- Validate against real wastewater treatment data  

---

## 📚 Reference
Project based on EBPR metabolic modeling framework and constraint-based analysis concepts. :contentReference[oaicite:0]{index=0}

---

## 👨‍💻 Author
[Your Name]

---

## 📌 Notes
This is a simplified model and serves as a conceptual framework for understanding EBPR metabolic switching under controlled conditions.
