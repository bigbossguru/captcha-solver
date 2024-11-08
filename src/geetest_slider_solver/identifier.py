import io

import cv2
import requests
import numpy as np
from PIL import Image


class GeeTestIdentifier:
    def __init__(self, background, puzzle_piece, debugger=False):
        self.background = self._read_image(background)
        self.puzzle_piece = self._read_image(puzzle_piece)
        self.debugger = debugger

    @staticmethod
    def test(background_url: str, slice_url: str):
        data = GeeTestIdentifier.load_test(background_url, slice_url)
        identifier = GeeTestIdentifier(
            background=GeeTestIdentifier.load_image(data["background"]),
            puzzle_piece=GeeTestIdentifier.load_image(data["puzzle"]),
            debugger=False,
        )
        result = identifier.find_puzzle_piece_position()
        return result

    @staticmethod
    def load_image(url: str) -> np.ndarray:
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    @staticmethod
    def load_test(url_bg, url_slice):
        return {
            "background": url_bg,
            "puzzle": url_slice,
        }

    def _read_image(self, image_source):
        """
        Read an image from a file or a requests response object.
        """
        if isinstance(image_source, bytes):
            return cv2.imdecode(
                np.frombuffer(image_source, np.uint8), cv2.IMREAD_ANYCOLOR
            )
        elif hasattr(image_source, "read"):
            return cv2.imdecode(
                np.frombuffer(image_source.read(), np.uint8), cv2.IMREAD_ANYCOLOR
            )
        else:
            raise TypeError(
                "Invalid image source type. Must be bytes or a file-like object."
            )

    def find_puzzle_piece_position(self):
        """
        Find the matching position of a puzzle piece in a background image.
        """
        # Apply edge detection
        edge_puzzle_piece = cv2.Canny(self.puzzle_piece, 100, 200)
        edge_background = cv2.Canny(self.background, 100, 200)

        # Convert to RGB for visualization
        edge_puzzle_piece_rgb = cv2.cvtColor(edge_puzzle_piece, cv2.COLOR_GRAY2RGB)
        edge_background_rgb = cv2.cvtColor(edge_background, cv2.COLOR_GRAY2RGB)

        # Template matching
        res = cv2.matchTemplate(
            edge_background_rgb, edge_puzzle_piece_rgb, cv2.TM_CCOEFF_NORMED
        )
        _, _, _, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc
        h, w = edge_puzzle_piece.shape[:2]
        bottom_right = (top_left[0] + w, top_left[1] + h)

        # Calculate required values
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        position_from_left = center_x
        position_from_bottom = self.background.shape[0] - center_y

        # Draw rectangle, lines, and coordinates if debugger is True
        if self.debugger:
            cv2.imwrite("input.png", self.background)
            cv2.rectangle(self.background, top_left, bottom_right, (0, 0, 255), 2)
            cv2.line(
                self.background,
                (center_x, 0),
                (center_x, edge_background_rgb.shape[0]),
                (0, 255, 0),
                2,
            )
            cv2.line(
                self.background,
                (0, center_y),
                (edge_background_rgb.shape[1], center_y),
                (0, 255, 0),
                2,
            )
            cv2.imwrite("output.png", self.background)

        return {
            "position_from_left": position_from_left,
            "position_from_bottom": position_from_bottom,
            "coordinates": [center_x, center_y],
        }

    def get_puzzle_piece_box(self, img_bytes: bytes):
        """
        Identify the bounding box of the non-transparent part of an image.
        """
        image = Image.open(io.BytesIO(img_bytes))
        bbox = image.getbbox()
        cropped_image = image.crop(bbox)
        self.center = (bbox[3] - bbox[1]) // 2
        return cropped_image, bbox[0], bbox[1]
