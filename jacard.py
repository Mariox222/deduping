
class Jaccard:

    def __init__(self):
        pass

    def _jaccard(self, set1, set2):
        """ Calculate Jaccard Similarity.

        Args:
            set1 (set): Set of values.
            set2 (set): Set of values.

        Returns:
            float: Jaccard Similarity.

        """
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    @staticmethod
    def jaccard(set1, set2):
        """ Calculate Jaccard Similarity.

        Args:
            set1 (set): Set of values.
            set2 (set): Set of values.

        Returns:
            float: Jaccard Similarity.

        """
        return Jaccard()._jaccard(set1, set2)



