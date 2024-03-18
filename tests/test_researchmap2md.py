import unittest

from researchmap2md.researchmap2md import researchmap2csv


class TestSimple(unittest.TestCase):

    def test_researchmap2csv(self):
        researchmap2csv('resources/rm_presentations.csv')
        researchmap2csv('resources/rm_published_papers.csv')


if __name__ == '__main__':
    unittest.main()
