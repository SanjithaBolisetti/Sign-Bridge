import { useEffect, useRef, useState } from 'react'
import Webcam from 'react-webcam'
import './SignToText.css'

const PREDICT_URL = 'http://127.0.0.1:8000/predict'

function SignToText() {
  const webcamRef = useRef(null)
  const [prediction, setPrediction] = useState('—')
  const [confidence, setConfidence] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    return () => {
      // No interval cleanup needed; single-shot capture mode.
    }
  }, [])

  const captureOnce = async () => {
    if (!webcamRef.current) return
    const dataUrl = webcamRef.current.getScreenshot()
    if (!dataUrl) {
      setError('Unable to capture from camera')
      return
    }

    setLoading(true)
    setError('')
    try {
      const blob = await (await fetch(dataUrl)).blob()
      const formData = new FormData()
      formData.append('file', blob, 'frame.jpg')

      const res = await fetch(PREDICT_URL, {
        method: 'POST',
        body: formData,
      })

      const json = await res.json()
      setPrediction(json?.prediction ?? '—')
      setConfidence(typeof json?.confidence === 'number' ? json.confidence : null)
    } catch (err) {
      setError('Failed to send frame')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="hero">
        <p className="eyebrow">Sign to Text</p>
        <h2 className="section-title">Real-time Recognition</h2>

        <div className="webcam-wrap">
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            screenshotQuality={0.9}
            screenshotWidth={640}
            className="webcam"
            videoConstraints={{ width: 640, height: 480, facingMode: 'user' }}
          />
        </div>

        <div className="actions">
          <button type="button" className="primary" onClick={captureOnce} disabled={loading}>
            {loading ? 'Capturing…' : 'Capture & Predict'}
          </button>
        </div>

        <div className="prediction-box">
          <div className="label">Predicted Sign</div>
          <div className="value">{prediction}</div>
          <div className="confidence">
            Confidence: {confidence !== null ? (confidence * 100).toFixed(2) + '%' : '—'}
          </div>
          {loading ? <div className="loading">Running model…</div> : null}
          {error ? <div className="error">{error}</div> : null}
        </div>
      </div>
    </div>
  )
}

export default SignToText
