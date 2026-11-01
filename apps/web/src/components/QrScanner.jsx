import { useEffect, useId, useRef, useState } from "react";

/** Camera QR scanner with a paste fallback. Calls onResult once per scan. */
export default function QrScanner({ onResult, label = "Scan QR code" }) {
  const id = useId().replace(/:/g, "");
  const [scanning, setScanning] = useState(false);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [paste, setPaste] = useState("");
  const scanner = useRef(null);
  const handledScan = useRef(false);
  const startingRef = useRef(false);

  useEffect(() => () => {
    const active = scanner.current;
    if (active?.isScanning) active.stop().catch(() => {});
  }, []);

  const stop = async () => {
    const active = scanner.current;
    if (active?.isScanning) await active.stop().catch(() => {});
    setScanning(false);
    setStatus("");
  };

  const start = async () => {
    if (startingRef.current || scanner.current?.isScanning) return;
    startingRef.current = true;
    setStarting(true);
    setError("");
    setStatus("Opening camera…");
    handledScan.current = false;
    try {
      const { Html5Qrcode } = await import("html5-qrcode");
      const active = new Html5Qrcode(`qr-${id}`);
      scanner.current = active;
      setScanning(true);
      const onScan = async (text) => {
        if (handledScan.current) return;
        handledScan.current = true;
        setStatus("QR detected. Processing…");
        await active.stop().catch(() => {});
        setScanning(false);
        try {
          await onResult(text);
          setStatus("QR detected.");
        } catch (scanError) {
          setStatus("");
          setError(scanError?.message || "QR detected, but this code could not be used here.");
        }
      };
      // Scan the whole frame so dense receipt codes need not fit a small box.
      const options = { fps: 10 };
      try {
        await active.start({ facingMode: "environment" }, options, onScan);
      } catch (rearError) {
        const cameras = await Html5Qrcode.getCameras();
        if (!cameras.length) throw rearError;
        const rear = cameras.find((camera) => /back|rear|environment/i.test(camera.label));
        await active.start((rear || cameras[0]).id, options, onScan);
      }
      setStatus("Camera is on. Hold the whole QR code steady in view.");
    } catch (cameraError) {
      if (scanner.current?.isScanning) await scanner.current.stop().catch(() => {});
      setScanning(false);
      setStatus("");
      setError(explainCameraError(cameraError));
    } finally {
      startingRef.current = false;
      setStarting(false);
    }
  };

  return (
    <div className="qr-scanner">
      <div id={`qr-${id}`} className="qr-camera" hidden={!scanning} />
      <div className="qr-controls">
        {starting ? (
          <button type="button" className="button outline" disabled>Opening camera…</button>
        ) : scanning ? (
          <button type="button" className="button outline" onClick={stop}>Stop camera</button>
        ) : (
          <button type="button" className="button" onClick={start}>📷 {label}</button>
        )}
      </div>
      {status && <p className="qr-scan-status" role="status">{status}</p>}
      {error && <p className="feedback error" role="alert">{error}</p>}
      <div className="qr-controls">
        <input
          className="mono"
          aria-label="QR code"
          placeholder="…or paste the code"
          value={paste}
          onChange={(e) => setPaste(e.target.value)}
        />
        <button
          type="button"
          className="button outline"
          disabled={!paste.trim()}
          onClick={async () => {
            const text = paste.trim();
            setPaste("");
            try {
              await onResult(text);
              setError("");
              setStatus("Code received.");
            } catch (pasteError) {
              setError(pasteError?.message || "This code could not be used here.");
            }
          }}
        >
          Use
        </button>
      </div>
    </div>
  );
}

function explainCameraError(error) {
  const detail = String(error?.message || error || "Unknown error");
  if (!globalThis.isSecureContext)
    return "Camera access needs HTTPS. Open the phone’s Tailscale HTTPS address.";
  if (/NotAllowedError|PermissionDeniedError|Permission denied/i.test(detail))
    return `Camera request was rejected: ${detail.slice(0, 180)}. Device camera access may be blocked even when site access is allowed.`;
  if (/NotReadableError|TrackStartError|Could not start video source/i.test(detail))
    return `Camera could not open: ${detail.slice(0, 180)}. Close other camera apps and retry.`;
  return `Camera could not start: ${detail.slice(0, 180)}`;
}
