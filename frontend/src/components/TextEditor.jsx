import './TextEditor.css'

function TextEditor({ value, onChange, disabled }) {
  return (
    <div className="text-editor-wrapper">
      <div className="editor-header">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 7H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          <path d="M4 12H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          <path d="M4 17H14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
        <span>Enter your text</span>
      </div>
      <textarea
        className="text-editor"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste your text here...
Example: The color of silence tastes loud. He was born in 2010. He voted in 1999. Hello how are you"
        disabled={disabled}
        rows={10}
      />
    </div>
  )
}

export default TextEditor