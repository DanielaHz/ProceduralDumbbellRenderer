# Procedural Rendering With Python and Renderman 

The project focuses on the development and implementation of custom shaders for the procedural rendering of a 3D dumbbell model, using the RenderMan renderingengine and the Python API

![image](/images/Dumbbell_1.png)


## Runthe program 
```
uv run python Scene.py
```

## Dumbbell Model Reference

![image](/images/Real.jpeg)

## Commands to Compile shaders and textures

Compiling textures
```
txmake input.exr output.tex
```

Compiling Shaders

```
oslc input.osl
```

Printing information of the shaders and textures
```
oslinfo PxrBump.oso
```
```
txinfo ckdkj.tex
```

## References
- https://polyhaven.com/a/courtyard
- https://www.youtube.com/watch?v=Bx67s2VL7rI&t=1s&ab_channel=RyanKingArt
- https://repfitness.com/blogs/guides/more-than-you-ever-wanted-to-know-about-knurling
