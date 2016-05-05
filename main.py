from shot_detector import ShotBoundaryDetector

if __name__ == '__main__':
    detector = ShotBoundaryDetector('BlueUmbrella.webm')
    detector.detect()
