import unittest

from pyslam.indirection import CategoryMapper, Indirection


class TestCategoryMapper(unittest.TestCase):

    def setUp(self):
        # Initialisation des objets nécessaires pour les tests
        self.mapper = CategoryMapper()
        self.imapper = CategoryMapper({'A': 0, 'B': 1, 'C': 2})
        self.indirections = {
            10: ['Alpha', 'Beta', 'Gamma'],
            20: ['One', 'Two', 'Three']
        }
        self.indirection = Indirection(self.imapper, self.indirections)

    def test_initialization(self):
        # Test d'initialisation avec des valeurs
        mapper = CategoryMapper({'A': 1, 'B': 2})
        self.assertEqual(mapper['A'], 1)
        self.assertEqual(mapper.get_key(1), 'A')

    def test_add_item(self):
        # Test d'ajout d'une paire clé-valeur
        self.mapper['C'] = 3
        self.assertEqual(self.mapper['C'], 3)
        self.assertEqual(self.mapper.get_key(3), 'C')

    def test_update_item(self):
        # Test de mise à jour d'une paire clé-valeur existante
        self.mapper['D'] = 4
        self.mapper['D'] = 5
        self.assertEqual(self.mapper['D'], 5)
        self.assertEqual(self.mapper.get_key(5), 'D')
        self.assertIsNone(self.mapper.get_key(4))

    def test_delete_item(self):
        # Test de suppression d'une paire clé-valeur
        self.mapper['E'] = 6
        del self.mapper['E']
        self.assertNotIn('E', self.mapper)
        self.assertIsNone(self.mapper.get_key(6))

    def test_get_key_nonexistent(self):
        # Test de récupération d'une clé pour une valeur inexistante
        self.assertIsNone(self.mapper.get_key(99))

    def test_out_value_success(self):
        # Test avec des valeurs valides
        self.assertEqual(self.indirection.out_value('A', 10), 'Alpha')
        self.assertEqual(self.indirection.out_value('B', 20), 'Two')

    def test_out_value_invalid_in_value(self):
        # Test avec une valeur in_value invalide
        with self.assertRaises(AssertionError):
            self.indirection.out_value('A', 30)

    def test_out_value_invalid_key(self):
        # Test avec une clé invalide
        with self.assertRaises(AssertionError):
            self.indirection.out_value('D', 10)

    def test_out_value_invalid_mapping(self):
        # Test avec une clé valide mais une valeur in_value invalide
        with self.assertRaises(IndexError):
            # Supposons que 'A' mappe à 3, ce qui est hors de portée pour la liste
            self.imapper['A'] = 3
            self.indirection.out_value('A', 10)


if __name__ == "__main__":
    unittest.main()
