import os
import tempfile
from unittest import TestCase
from ansible_inventory_editor.editor import AnsibleInventoryEditor

class TestAnsibleInventoryEditor(TestCase):
    empty_file = os.path.join(tempfile.gettempdir(), "tmp-empty-file.yaml")
    hosts_file = os.path.join(tempfile.gettempdir(), "tmp-hosts-file.yaml")
    
    def setUp(self):
        with open(self.empty_file, "wb") as f:
            f.write("")
            
        with open(self.hosts_file, "wb") as f:
            f.write()
    
    def tearDown(self):
        os.remove(self.empty_file)
        os.remove(self.hosts_file)
    
    def test_check_if_hostname_is_taken(self):

        a = AnsibleInventoryEditor()
        

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
    