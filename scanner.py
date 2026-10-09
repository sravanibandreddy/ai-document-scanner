
import cv2
import numpy as np


def order_points(points):
    """Arrange four corners: top-left, top-right,
    bottom-right, bottom-left."""
    points = np.asarray(points, dtype="float32")
    ordered = np.zeros((4, 2), dtype="float32")

    sums = points.sum(axis=1)
    differences = np.diff(points, axis=1).ravel()

    ordered[0] = points[np.argmin(sums)]
    ordered[2] = points[np.argmax(sums)]
    ordered[1] = points[np.argmin(differences)]
    ordered[3] = points[np.argmax(differences)]

    return ordered


def scan_document(image_path, output_path="scanned.png"):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    original = image.copy()
    ratio = image.shape[0] / 700.0
    resized = cv2.resize(image, (int(image.shape[1] / ratio), 700))

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(
        edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    corners = None

    for contour in contours[:10]:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

        if len(approx) == 4:
            corners = approx.reshape(4, 2).astype("float32") * ratio
            break

    if corners is None:
        print("Document boundary not detected; saving original image.")
        result = original
    else:
        rect = order_points(corners)
        top_left, top_right, bottom_right, bottom_left = rect

        width = int(max(
            np.linalg.norm(bottom_right - bottom_left),
            np.linalg.norm(top_right - top_left)
        ))
        height = int(max(
            np.linalg.norm(top_right - bottom_right),
            np.linalg.norm(top_left - bottom_left)
        ))

        if width < 2 or height < 2:
            raise ValueError("Detected document boundary is too small.")

        destination = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]
        ], dtype="float32")

        transform = cv2.getPerspectiveTransform(rect, destination)
        result = cv2.warpPerspective(original, transform, (width, height))

    if not cv2.imwrite(output_path, result):
        raise ValueError(f"Could not save output: {output_path}")

    print(f"Scanned image saved to: {output_path}")
    return result


if __name__ == "__main__":
    scan_document("document_photo.jpg")