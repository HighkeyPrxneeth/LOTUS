import { useEffect, useRef, useState } from "react";
import { QRCodeSVG } from "qrcode.react";

export default function QrDisplay({ value, size = 320 }) {
  const [open, setOpen] = useState(false);
  const dialogRef = useRef(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <>
      <div className="qr-wrap">
        <QRCodeSVG value={value} size={size} marginSize={4} />
      </div>
      <button type="button" className="button outline small" onClick={() => setOpen(true)}>
        Enlarge QR for scanning
      </button>
      <dialog ref={dialogRef} className="qr-zoom-dialog" onClose={() => setOpen(false)}>
        <button type="button" className="button outline small" onClick={() => setOpen(false)}>
          Close large QR
        </button>
        <QRCodeSVG value={value} size={600} marginSize={4} />
        <p>Keep the whole square visible on the laptop screen while the phone camera focuses.</p>
      </dialog>
    </>
  );
}
