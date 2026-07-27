# Generated diagrams

SVG and PNG files in this directory are generated from every `.puml` source under `C4/` by:

```bash
bash scripts/render-diagrams.sh
```

The canonical sources are the `.puml` files. Generated images are committed so GitHub Pages can display the PNG immediately and link the reader to the corresponding SVG.

Documentation convention:

```md
[![Diagram](../assets/diagrams/example.png)](../assets/diagrams/example.svg)

[**Abrir diagrama em SVG**](../assets/diagrams/example.svg)
```
