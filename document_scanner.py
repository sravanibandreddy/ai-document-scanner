
import cv2
import numpy as np


def order_points(points):
    points = np.asarray(points, dtype="float32")
    result = np.zeros((4, 2), dtype="float32")

    sums = points.sum(axis=1)
    diffs = np.diff(points, axis=1).reshape(-1)

    result[0] = points[np.argmin(sums)]   # Top-left
    result[1] = points[np.argmin(diffs)]  # Top-right
    result[2] = points[np.argmax(sums)]   # Bottom-right
    result[3] = points[np.argmax(diffs)]  # Bottom-left

    return result


def scan_document(image):
    if image is None:
        raise ValueError("Input image is empty.")

    original = image.copy()
    height, width = image.shape[:2]

    # Resize only for detection
    scale = min(700 / max(height, width), 1.0)
    resized = cv2.resize(
        image,
        (int(width * scale), int(height * scale))
    )

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True
    )

    detected = None
    image_area = resized.shape[0] * resized.shape[1]

    for contour in contours[:10]:
        area = cv2.contourArea(contour)

        # Ignore very small contours and near-full-image borders
        if area < image_area * 0.10:
            continue
        if area > image_area * 0.95:
            continue

        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(
            contour, 0.02 * perimeter, True
        )

        if len(approx) == 4:
            detected = approx.reshape(4, 2)
            break

    if detected is None:
        print("No reliable document boundary found; using original image.")
        return original

    # Map detected points to the original image
    rect = order_points(detected / scale)
    tl, tr, br, bl = rect

    out_width = int(max(
        np.linalg.norm(br - bl),
        np.linalg.norm(tr - tl)
    ))
    out_height = int(max(
        np.linalg.norm(tr - br),
        np.linalg.norm(tl - bl)
    ))

    if out_width < 50 or out_height < 50:
        return original

    destination = np.array([
        [0, 0],
        [out_width - 1, 0],
        [out_width - 1, out_height - 1],
        [0, out_height - 1]
    ], dtype="float32")

    matrix = cv2.getPerspectiveTransform(rect, destination)

    corrected = cv2.warpPerspective(
        original,
        matrix,
        (out_width, out_height)
    )

    return corrected


if __name__ == "__main__":
    image = cv2.imread("document_photo.jpg")

    if image is None:
        print("Test image document_photo.jpg was not found.")
    else:
        scanned = scan_document(image)
        cv2.imwrite("scanned_document.png", scanned)
        print("Saved scanned_document.png")
