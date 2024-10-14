from utahwaterpoloassociation.generator import Generator


if __name__ == "__main__":
    generate = Generator()
    generate.load_pages()
    generate.render()
