import unittest
from imageio import imread as libread

from Morphing import *

TestFolder = "TestData"


def imread(filePath):
    startImage = libread(filePath)
    return np.array(startImage)


class MorphingTestSuite(unittest.TestCase):

    def test_loadTriangle(self):

        leftPath = os.path.join(TestFolder, "points.left.txt")
        rightPath = os.path.join(TestFolder, "points.right.txt")
        loaded = loadTriangles(leftPath, rightPath)

        with self.subTest(key="Returned Type"):

            self.assertIsInstance(loaded, tuple)

        first, second = loaded

        with self.subTest(key="Triangles present"):

            isValid1 = all(isinstance(e, Triangle) for e in first)
            isValid2 = all(isinstance(e, Triangle) for e in second)
            self.assertTrue(isValid1 and isValid2)

    def test_Triangle(self):

        with self.subTest(key="Normal Initializer"):

            t = Triangle(self.support.vertices)
            self.assertIsInstance(t, Triangle)

        with self.subTest(key="Incorrect Dimensions"):

            self.assertRaises(ValueError, Triangle, self.support.smallVertices)

        with self.subTest(key="Incorrect DataType"):

            self.assertRaises(ValueError, Triangle, self.support.otherVertices)

        with self.subTest(key="Incorrect Types"):

            self.assertRaises(ValueError, Triangle, [[786.6, 864.], [844.2, 898.2], [709.2, 1079.]])

        with self.subTest(key="Point Content"):             # 11 Points
            tri = Triangle(self.support.pointVertices)
            actualValue = sorted([(int(x), int(y)) for x, y in tri.getPoints().tolist()])
            expectedValue = sorted([(int(x), int(y)) for x, y in self.support.samplePoints.tolist()])

            actualPoints = set(actualValue)
            expectedPoints = set(expectedValue)
            common = actualPoints & expectedPoints
            difference = (actualPoints - expectedPoints) | (expectedPoints - actualPoints)

            if difference:
                print(f" ==> Common Points = {len(common)}, Different Points = {len(difference)}")
                print(f" =====> List of different points = {difference}\n")

            self.assertLessEqual(len(difference), 35)

    def test_Morpher(self):

        leftPointFilePath = os.path.join(TestFolder, "points.left.txt")
        rightPointFilePath = os.path.join(TestFolder, "points.right.txt")
        leftTriangles, rightTriangles = loadTriangles(leftPointFilePath, rightPointFilePath)

        leftImagePath = os.path.join(TestFolder, 'LeftGray.png')
        rightImagePath = os.path.join(TestFolder, 'RightGray.png')

        leftImage = imread(leftImagePath)
        rightImage = imread(rightImagePath)

        morpher = Morpher(leftImage, leftTriangles, rightImage, rightTriangles)

        with self.subTest(key="Normal Initializer"):

            self.assertIsInstance(morpher, Morpher)

        with self.subTest(key="Attribute Check"):

            attributes = ["leftImage", "leftTriangles", "rightImage", "rightTriangles"]
            actualValue = all(hasattr(morpher, a) for a in attributes)
            self.assertTrue(actualValue)

        with self.subTest(key="Incorrect Initializer"):

            arr = self.support.pointVertices
            self.assertRaises(TypeError, Morpher, leftImage, arr, rightImage, arr)

        with self.subTest(key="Blending Type"):

            blended = morpher.getImageAtAlpha(0.67)

            self.assertIsInstance(blended, np.ndarray)



    @classmethod
    def setUpClass(cls):
        cls.support = Support()


class Support:

    def __init__(self):
        filePath = os.path.join(TestFolder, 'Support.npz')
        with np.load(filePath) as dataFile:
            self.vertices = dataFile["vertices"]
            self.smallVertices = dataFile["smallVertices"]
            self.otherVertices = dataFile["otherVertices"]

            self.pointVertices = dataFile["pointVertices"]
            self.samplePoints = dataFile["samplePoints"]


if __name__ == '__main__':
    unittest.main()
