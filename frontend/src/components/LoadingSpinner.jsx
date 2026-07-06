import './LoadingSpinner.css'

function LoadingSpinner({ message = "Analyzing..." }) {
  return (
    <div className="loading-spinner">
      <div className="spinner"></div>
      <p>{message}</p>
    </div>
  )
}

export default LoadingSpinner