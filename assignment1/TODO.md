# TODO: Markov Model Text Analysis Project

## 1. Implement `fcm` Program
- [ ] Create program structure (C/C++/Rust)
- [ ] Implement text file input handling
- [ ] Build frequency table for k-length contexts
- [ ] Implement probability calculation with smoothing: P(e|c) = (N(e|c) + α) / (∑(N(s|c) + α|Σ|))
- [ ] Calculate average information content: Hₙ = -(1/n) ∑ log₂P(xᵢ|c)
- [ ] Implement command-line parameter handling (k, α)
- [ ] Output theoretical information content in bits per symbol (bps)
- [ ] Add error handling and validation
- [ ] Test with sample text files

## 2. Implement `generator` Program
- [ ] Create program structure
- [ ] Implement Markov model learning from training text
- [ ] Build probability tables based on frequency analysis
- [ ] Handle starting context (prior) parameter
- [ ] Implement text generation algorithm using learned probabilities
- [ ] Add command-line parameter handling (k, α, prior, sequence length)
- [ ] Add error handling and validation
- [ ] Test with various parameters and training texts

## 3. Write Analysis Report
- [ ] Document implementation details and design choices
- [ ] Analyze how different texts affect average information content
- [ ] Study and document the effects of varying k and α parameters
- [ ] Compare results across the mandatory text files (sequence1.txt through sequence5.txt)
- [ ] Include visualizations or tables to illustrate findings
- [ ] Draw conclusions about model effectiveness
- [ ] Format as PDF

## 4. Prepare GitHub Repository
- [ ] Initialize repository with appropriate structure
- [ ] Add source code for both programs
- [ ] Include test text files
- [ ] Create comprehensive README.md with:
  - [ ] Project overview
  - [ ] Installation instructions
  - [ ] Dependency details
  - [ ] Compilation steps
  - [ ] Usage examples with sample commands
  - [ ] Parameter explanations
- [ ] Add final report (PDF format)
- [ ] Include license information
- [ ] Organize repository for clear navigation
- [ ] Prepare email with repository link or ZIP file for submission

## Mathematical Formulas Reference
- Probability calculation: P(e|c) = (N(e|c) + α) / (∑(N(s|c) + α|Σ|))
- Average information content: Hₙ = -(1/n) ∑ log₂P(xᵢ|c)