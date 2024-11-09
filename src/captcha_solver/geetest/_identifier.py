import cv2
import requests
import numpy as np


class GeeTestIdentifier:
    def __init__(self, background_url: str, puzzle_url: str, debugger=False):
        self.background_img = self._load_image(background_url)
        self.puzzle_img = self._load_image(puzzle_url)
        self.background = self._read_image(self.background_img)
        self.puzzle_piece = self._read_image(self.puzzle_img)
        self.debugger = debugger

    def _load_image(self, url: str) -> np.ndarray:
        response = requests.get(url)
        response.raise_for_status()
        return response.content

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

    def find_puzzle_position(self):
        """
        Find the matching position of a puzzle piece in a background image.
        """
        edge_puzzle_piece = cv2.Canny(self.puzzle_piece, 100, 200)
        edge_background = cv2.Canny(self.background, 100, 200)

        edge_puzzle_piece_rgb = cv2.cvtColor(edge_puzzle_piece, cv2.COLOR_GRAY2RGB)
        edge_background_rgb = cv2.cvtColor(edge_background, cv2.COLOR_GRAY2RGB)

        res = cv2.matchTemplate(
            edge_background_rgb, edge_puzzle_piece_rgb, cv2.TM_CCOEFF_NORMED
        )
        _, _, _, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc
        h, w = edge_puzzle_piece.shape[:2]
        bottom_right = (top_left[0] + w, top_left[1] + h)

        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        position_from_left = center_x
        position_from_bottom = self.background.shape[0] - center_y

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
