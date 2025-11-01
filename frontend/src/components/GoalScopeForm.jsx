import { useState } from 'react'
import './GoalScopeForm.css'

/**
 * ISO 14040/14044 Goal and Scope Definition Form
 *
 * This component implements the Goal and Scope definition requirements
 * from ISO 14044:2006 Section 4.2.
 */
function GoalScopeForm({ onSave, onCancel, initialData = null }) {
  // Initialize form state
  const [formData, setFormData] = useState(initialData || {
    study_id: `study_${Date.now()}`,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),

    // Goal definition (ISO 14044 Section 4.2.2)
    study_goal: '',
    reasons_for_study: '',
    intended_audience: '',
    comparative_assertion: false,

    // Functional Unit (ISO 14044 Section 4.2.3.2)
    functional_unit: {
      description: '',
      quantified_performance: '',
      reference_flow: '',
      amount: 1.0,
      unit: 'kg'
    },

    // System Boundary (ISO 14044 Section 4.2.3.3)
    system_boundary: {
      description: '',
      cut_off_criteria: '',
      included_processes: [],
      excluded_processes: []
    },

    // Data Quality (ISO 14044 Section 4.2.3.6)
    data_quality_requirements: {
      temporal_coverage: '',
      geographical_coverage: '',
      technological_coverage: '',
      precision: '',
      completeness: '',
      representativeness: '',
      consistency: '',
      reproducibility: '',
      data_sources: [],
      uncertainty_assessment: ''
    },

    assumptions: [],
    limitations: [],
    allocation_rules: [],
    impact_method: 'ILCD 2011 Midpoint'
  })

  const [currentStep, setCurrentStep] = useState(1)
  const [newItem, setNewItem] = useState('')

  const handleInputChange = (path, value) => {
    setFormData(prev => {
      const newData = { ...prev }
      const keys = path.split('.')
      let current = newData

      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]]
      }

      current[keys[keys.length - 1]] = value
      return newData
    })
  }

  const handleAddToList = (path) => {
    if (!newItem.trim()) return

    setFormData(prev => {
      const newData = { ...prev }
      const keys = path.split('.')
      let current = newData

      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]]
      }

      current[keys[keys.length - 1]] = [...current[keys[keys.length - 1]], newItem.trim()]
      return newData
    })

    setNewItem('')
  }

  const handleRemoveFromList = (path, index) => {
    setFormData(prev => {
      const newData = { ...prev }
      const keys = path.split('.')
      let current = newData

      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]]
      }

      current[keys[keys.length - 1]] = current[keys[keys.length - 1]].filter((_, i) => i !== index)
      return newData
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    try {
      const response = await fetch('http://localhost:8000/api/goal-scope', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          updated_at: new Date().toISOString()
        })
      })

      if (!response.ok) {
        throw new Error('Failed to save Goal & Scope')
      }

      const result = await response.json()
      onSave(result)
    } catch (error) {
      console.error('Error saving Goal & Scope:', error)
      alert('Failed to save Goal & Scope: ' + error.message)
    }
  }

  const renderStep1 = () => (
    <div className="form-section">
      <h3>Goal Definition</h3>
      <p className="iso-ref">ISO 14044:2006 Section 4.2.2</p>

      <div className="form-group">
        <label htmlFor="study_goal">
          Study Goal *
          <span className="help-text">Intended application and reasons for carrying out the study</span>
        </label>
        <textarea
          id="study_goal"
          value={formData.study_goal}
          onChange={(e) => handleInputChange('study_goal', e.target.value)}
          required
          rows={3}
          placeholder="e.g., To assess the environmental impacts of glass fiber production for use in comparative assertions..."
        />
      </div>

      <div className="form-group">
        <label htmlFor="reasons_for_study">
          Reasons for Study *
        </label>
        <textarea
          id="reasons_for_study"
          value={formData.reasons_for_study}
          onChange={(e) => handleInputChange('reasons_for_study', e.target.value)}
          required
          rows={2}
          placeholder="e.g., To identify environmental hotspots and improvement opportunities..."
        />
      </div>

      <div className="form-group">
        <label htmlFor="intended_audience">
          Intended Audience *
        </label>
        <input
          type="text"
          id="intended_audience"
          value={formData.intended_audience}
          onChange={(e) => handleInputChange('intended_audience', e.target.value)}
          required
          placeholder="e.g., Internal management, public stakeholders, regulatory bodies..."
        />
      </div>

      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.comparative_assertion}
            onChange={(e) => handleInputChange('comparative_assertion', e.target.checked)}
          />
          Results will be used for public comparative assertions
          <span className="help-text">If checked, critical review is required (ISO 14044 Section 6)</span>
        </label>
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="form-section">
      <h3>Functional Unit</h3>
      <p className="iso-ref">ISO 14044:2006 Section 4.2.3.2</p>
      <p className="iso-note">
        The functional unit defines the quantification of the identified functions (performance characteristics)
        of the product system. It provides a reference to which the inputs and outputs are related.
      </p>

      <div className="form-group">
        <label htmlFor="fu_description">
          Description *
        </label>
        <input
          type="text"
          id="fu_description"
          value={formData.functional_unit.description}
          onChange={(e) => handleInputChange('functional_unit.description', e.target.value)}
          required
          placeholder="e.g., Production and delivery of 1 kg of glass fiber composite"
        />
      </div>

      <div className="form-group">
        <label htmlFor="fu_performance">
          Quantified Performance *
          <span className="help-text">What function does the product provide?</span>
        </label>
        <input
          type="text"
          id="fu_performance"
          value={formData.functional_unit.quantified_performance}
          onChange={(e) => handleInputChange('functional_unit.quantified_performance', e.target.value)}
          required
          placeholder="e.g., Manufacturing and delivery of composite material for construction"
        />
      </div>

      <div className="form-group">
        <label htmlFor="fu_reference_flow">
          Reference Flow *
          <span className="help-text">The flow that delivers this function</span>
        </label>
        <input
          type="text"
          id="fu_reference_flow"
          value={formData.functional_unit.reference_flow}
          onChange={(e) => handleInputChange('functional_unit.reference_flow', e.target.value)}
          required
          placeholder="e.g., Glass fiber reinforced polymer"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="fu_amount">Amount *</label>
          <input
            type="number"
            id="fu_amount"
            value={formData.functional_unit.amount}
            onChange={(e) => handleInputChange('functional_unit.amount', parseFloat(e.target.value))}
            required
            min="0"
            step="0.01"
          />
        </div>

        <div className="form-group">
          <label htmlFor="fu_unit">Unit *</label>
          <select
            id="fu_unit"
            value={formData.functional_unit.unit}
            onChange={(e) => handleInputChange('functional_unit.unit', e.target.value)}
            required
          >
            <option value="kg">kg</option>
            <option value="ton">ton</option>
            <option value="m3">m³</option>
            <option value="m2">m²</option>
            <option value="unit">unit</option>
            <option value="MJ">MJ</option>
          </select>
        </div>
      </div>
    </div>
  )

  const renderStep3 = () => (
    <div className="form-section">
      <h3>System Boundary & Data Quality</h3>
      <p className="iso-ref">ISO 14044:2006 Sections 4.2.3.3 & 4.2.3.6</p>

      <h4>System Boundary</h4>
      <div className="form-group">
        <label htmlFor="sb_description">
          Description *
        </label>
        <textarea
          id="sb_description"
          value={formData.system_boundary.description}
          onChange={(e) => handleInputChange('system_boundary.description', e.target.value)}
          required
          rows={2}
          placeholder="e.g., Cradle-to-gate, including raw material extraction, processing, and manufacturing..."
        />
      </div>

      <div className="form-group">
        <label htmlFor="sb_cutoff">
          Cut-off Criteria *
        </label>
        <input
          type="text"
          id="sb_cutoff"
          value={formData.system_boundary.cut_off_criteria}
          onChange={(e) => handleInputChange('system_boundary.cut_off_criteria', e.target.value)}
          required
          placeholder="e.g., Flows < 1% of mass or energy are excluded"
        />
      </div>

      <h4 style={{ marginTop: '2rem' }}>Data Quality</h4>
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="dq_temporal">Temporal Coverage *</label>
          <input
            type="text"
            id="dq_temporal"
            value={formData.data_quality_requirements.temporal_coverage}
            onChange={(e) => handleInputChange('data_quality_requirements.temporal_coverage', e.target.value)}
            required
            placeholder="e.g., 2020-2023"
          />
        </div>

        <div className="form-group">
          <label htmlFor="dq_geographical">Geographical Coverage *</label>
          <input
            type="text"
            id="dq_geographical"
            value={formData.data_quality_requirements.geographical_coverage}
            onChange={(e) => handleInputChange('data_quality_requirements.geographical_coverage', e.target.value)}
            required
            placeholder="e.g., European Union"
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="dq_technological">Technological Coverage *</label>
        <input
          type="text"
          id="dq_technological"
          value={formData.data_quality_requirements.technological_coverage}
          onChange={(e) => handleInputChange('data_quality_requirements.technological_coverage', e.target.value)}
          required
          placeholder="e.g., Average European technology"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="dq_completeness">Completeness *</label>
          <input
            type="text"
            id="dq_completeness"
            value={formData.data_quality_requirements.completeness}
            onChange={(e) => handleInputChange('data_quality_requirements.completeness', e.target.value)}
            required
            placeholder="e.g., 95%"
          />
        </div>

        <div className="form-group">
          <label htmlFor="dq_precision">Precision *</label>
          <input
            type="text"
            id="dq_precision"
            value={formData.data_quality_requirements.precision}
            onChange={(e) => handleInputChange('data_quality_requirements.precision', e.target.value)}
            required
            placeholder="e.g., ±10%"
          />
        </div>
      </div>
    </div>
  )

  const renderStep4 = () => (
    <div className="form-section">
      <h3>Assumptions, Limitations & Allocation</h3>

      <div className="list-group">
        <h4>Assumptions</h4>
        <div className="list-input">
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder="Add an assumption..."
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddToList('assumptions'))}
          />
          <button type="button" onClick={() => handleAddToList('assumptions')} className="btn-add">
            Add
          </button>
        </div>
        <ul className="list-items">
          {formData.assumptions.map((item, index) => (
            <li key={index}>
              {item}
              <button type="button" onClick={() => handleRemoveFromList('assumptions', index)} className="btn-remove">
                ×
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="list-group">
        <h4>Limitations</h4>
        <div className="list-input">
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder="Add a limitation..."
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddToList('limitations'))}
          />
          <button type="button" onClick={() => handleAddToList('limitations')} className="btn-add">
            Add
          </button>
        </div>
        <ul className="list-items">
          {formData.limitations.map((item, index) => (
            <li key={index}>
              {item}
              <button type="button" onClick={() => handleRemoveFromList('limitations', index)} className="btn-remove">
                ×
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="list-group">
        <h4>Allocation Rules</h4>
        <p className="help-text">How co-products are handled</p>
        <div className="list-input">
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder="Add an allocation rule..."
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddToList('allocation_rules'))}
          />
          <button type="button" onClick={() => handleAddToList('allocation_rules')} className="btn-add">
            Add
          </button>
        </div>
        <ul className="list-items">
          {formData.allocation_rules.map((item, index) => (
            <li key={index}>
              {item}
              <button type="button" onClick={() => handleRemoveFromList('allocation_rules', index)} className="btn-remove">
                ×
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="form-group">
        <label htmlFor="impact_method">LCIA Method *</label>
        <select
          id="impact_method"
          value={formData.impact_method}
          onChange={(e) => handleInputChange('impact_method', e.target.value)}
          required
        >
          <option value="ILCD 2011 Midpoint">ILCD 2011 Midpoint</option>
          <option value="ReCiPe 2016">ReCiPe 2016</option>
          <option value="CML 2001">CML 2001</option>
          <option value="TRACI 2.1">TRACI 2.1</option>
        </select>
      </div>
    </div>
  )

  return (
    <div className="goal-scope-form-overlay">
      <div className="goal-scope-form">
        <div className="form-header">
          <h2>Define Goal & Scope</h2>
          <p>ISO 14040/14044 Compliant Study Definition</p>
          <button type="button" className="btn-close" onClick={onCancel}>×</button>
        </div>

        <div className="step-indicator">
          <div className={`step ${currentStep >= 1 ? 'active' : ''} ${currentStep > 1 ? 'completed' : ''}`}>
            <span>1</span> Goal
          </div>
          <div className={`step ${currentStep >= 2 ? 'active' : ''} ${currentStep > 2 ? 'completed' : ''}`}>
            <span>2</span> Functional Unit
          </div>
          <div className={`step ${currentStep >= 3 ? 'active' : ''} ${currentStep > 3 ? 'completed' : ''}`}>
            <span>3</span> Boundary & Quality
          </div>
          <div className={`step ${currentStep >= 4 ? 'active' : ''} ${currentStep > 4 ? 'completed' : ''}`}>
            <span>4</span> Assumptions & Allocation
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-body">
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
            {currentStep === 4 && renderStep4()}
          </div>

          <div className="form-footer">
            <div className="footer-left">
              {currentStep > 1 && (
                <button type="button" onClick={() => setCurrentStep(currentStep - 1)} className="btn-secondary">
                  Previous
                </button>
              )}
            </div>
            <div className="footer-right">
              {currentStep < 4 ? (
                <button type="button" onClick={() => setCurrentStep(currentStep + 1)} className="btn-primary">
                  Next
                </button>
              ) : (
                <button type="submit" className="btn-primary">
                  Save Goal & Scope
                </button>
              )}
              <button type="button" onClick={onCancel} className="btn-secondary">
                Cancel
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default GoalScopeForm
