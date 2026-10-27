from viewer import panelsession


def test_rootNode():
    root_node = panelsession.RootNode()

    assert root_node.is_root
    assert root_node.label == "Root"
    assert root_node.strength == 0