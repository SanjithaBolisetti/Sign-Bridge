import { useEffect, useRef, useState } from 'react'
import Webcam from 'react-webcam'
import './SignToText.css'

const PREDICT_URL = 'http://127.0.0.1:8000/predict'
const CAPTURE_INTERVAL_MS = 1500

function SignToText() {
  const webcamRef = useRef(null)
  const intervalRef = useRef(null)
  const [prediction, setPrediction] = useState('—')
  const [confidence, setConfidence] = useState(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')

  const stopLoop = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setRunning(false)
  }

  useEffect(() => {
    return () => stopLoop()
  }, [])

  const sendFrame = async () => {
    if (!webcamRef.current) return
    const dataUrl = webcamRef.current.getScreenshot()
    if (!dataUrl) return

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
      setError('')
    } catch (err) {
      setError('Failed to send frame')
    }
  }

  const startLoop = () => {
    if (running) return
    setRunning(true)
    setError('')
    sendFrame()
    intervalRef.current = setInterval(sendFrame, CAPTURE_INTERVAL_MS)
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
            className="webcam"
            videoConstraints={{ facingMode: 'user' }}
          />
        </div>

        <div className="actions">
          <button type="button" className="primary" onClick={startLoop} disabled={running}>
            Start Prediction
          </button>
          <button type="button" className="ghost" onClick={stopLoop} disabled={!running}>
            Stop Prediction
          </button>
        </div>

        <div className="prediction-box">
          <div className="label">Predicted Sign</div>
          <div className="value">{prediction}</div>
          <div className="confidence">
            Confidence: {confidence !== null ? (confidence * 100).toFixed(2) + '%' : '—'}
          </div>
          {error ? <div className="error">{error}</div> : null}
        </div>
      </div>
    </div>
  )
}

export default SignToText
