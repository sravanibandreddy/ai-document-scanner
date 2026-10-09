
import cv2
import numpy as np


def order_points(points):
    points = np.asarray(points, dtype="float32")
    ordered = np.zeros((4, 2), dtype="float32")

    sums = points.sum(axis=1)
    differences = np.diff(points, axis=1).reshape(-1)

    ordered[0] = points[np.argmin(sums)]       # top-left
    ordered[2] = points[np.argmax(sums)]       # bottom-right
    ordered[1] = points[np.argmin(differences)]  # top-right
    ordered[3] = points[np.argmax(differences)]  # bottom-left

    return ordered


def scan_document(image):
    if image is None or image.size == 0:
        return image

    height, width = image.shape[:2]
    scale = min(1.0, 900 / max(height, width))

    if scale < 1:
        working = cv2.resize(
            image, None, fx=scale, fy=scale,
            interpolation=cv2.INTER_AREA
        )
    else:
        working = image.copy()

    gray = cv2.cvtColor(working, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(
        edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    image_area = working.shape[0] * working.shape[1]

    for contour in contours[:30]:
        perimeter = cv2.arcLength(contour, True)
        approximation = cv2.approxPolyDP(
            contour, 0.02 * perimeter, True
        )

        if len(approximation) != 4:
            continue

        if cv2.contourArea(approximation) < image_area * 0.12:
            continue

        points = approximation.reshape(4, 2).astype("float32")
        points /= scale
        rect = order_points(points)

        top_left, top_right, bottom_right, bottom_left = rect

        width_a = np.linalg.norm(bottom_right - bottom_left)
        width_b = np.linalg.norm(top_right - top_left)
        height_a = np.linalg.norm(top_right - bottom_right)
        height_b = np.linalg.norm(top_left - bottom_left)

        output_width = int(max(width_a, width_b))
        output_height = int(max(height_a, height_b))

        if output_width < 2 or output_height < 2:
            continue

        destination = np.array([
            [0, 0],
            [output_width - 1, 0],
            [output_width - 1, output_height - 1],
            [0, output_height - 1]
        ], dtype="float32")

        transform = cv2.getPerspectiveTransform(rect, destination)

        corrected = cv2.warpPerspective(
            image, transform, (output_width, output_height)
        )
        return corrected

    return image
