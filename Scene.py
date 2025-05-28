# import the python functions
import sys
import prman
import argparse
import os

sys.path.append("./common")
import ProcessCommandLine as cl

# Main rendering routine
def main(
    filename="dumbbell.rib",
    shadingrate=0.5,
    pixelvar=0.01,
    fov=48.0,
    width=1024,
    height=720,
    integrator="PxrPathTracer",
    integratorParams={},
):
    ########################################################################
    # RENDERMAN SETUP SECTION
    ########################################################################

    print("shading rate {} pixel variance {} using {} {}".format(shadingrate, pixelvar, integrator, integratorParams))
    ri = prman.Ri()

    ri.Begin(filename)
    ri.Display("neoprene_shader.exr", "file", "rgba")
    ri.Option("searchpath", {"string archive": "./assets/:@"}) #search in assets folder
    ri.Option("searchpath", {"string texture": "./textures/:@"}) #search in textures folder
    ri.Option("searchpath", {"string shader": "./postshaders/:@"}) #search in postshaders folder for compiled shaders

    ri.Display("rgb.exr", "it", "rgba")
    ri.Format(width, height, 1)

    ri.Hider("raytrace", {"int incremental": [1]})
    ri.ShadingRate(shadingrate)
    ri.PixelVariance(pixelvar)
    ri.Integrator(integrator, 'integrator', integratorParams)
    ri.Option("statistics", {"filename": ["stats.txt"]})
    ri.Option("statistics", {"endofframe": [1]})

    #######################################################################
    # CAMERA SETUP
    #######################################################################

    ri.Projection(ri.PERSPECTIVE, {ri.FOV: fov})
    ri.Translate(0.2, -0.6, 7.0)
    ri.Rotate(-30, 1, 0, 0)
    ri.Rotate(-25, 0, 1, 0)
    ri.Rotate(0, 0, 1, 0)
    ri.WorldBegin()

    #######################################################################
    # LIGHTING SECTION
    #######################################################################

    # Light1.Environment Light
    ri.TransformBegin()
    ri.AttributeBegin()

    ri.Rotate(-30, 0, 1, 0)
    ri.Declare("domeLight", "string")
    ri.Attribute("visibility", {"int indirect": [1], "int transmission": [1], "int camera": [0]})
    ri.Light("PxrDomeLight", "domeLight", {
        "string lightColorMap": "peppermint_powerplant_2_4k.tex",
        "float exposure": [0.5]
    })

    ri.AttributeEnd()
    ri.TransformEnd()

    # Light2. Key Light
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Declare("Light0", "string")
    ri.Translate(2, 8, -5)
    ri.Rotate(90, 0, 0, 1)
    ri.Rotate(-90, 0, 1, 0)
    ri.Light("PxrRectLight", "Light0", {"float intensity": 50})
    ri.AttributeEnd()
    ri.TransformEnd()

    # Light3. Fill Light
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Declare("Light1", "string")
    ri.Attribute("visibility", {"int camera": 0, "int transmission": 0})
    ri.Translate(-3, 5, -5)       
    ri.Rotate(30, 1, 0, 0)        
    ri.Rotate(-30, 0, 1, 0)    
    ri.Light("PxrRectLight", "Light1", {"float intensity": 20})
    ri.AttributeEnd()
    ri.TransformEnd()

    # Light4. Back Light
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Declare("Light2", "string")
    ri.Attribute("visibility", {"int camera": 0, "int transmission": 0}) 
    ri.Translate(6, 3, 0) 
    ri.Rotate (270, 0, 1, 0)
    ri.Light("PxrRectLight", "Light2", {"float intensity":10})
    ri.AttributeEnd()
    ri.TransformEnd()

    #######################################################################
    # MODEL SECTION
    #######################################################################

    #########
    # FLOOR
    #########

    ri.AttributeBegin()
    ri.TransformBegin()
    ri.Attribute("identifier", {"name": "floor"})
    
    # Little rug pattern
    ri.Pattern("PxrFractal", "carpetFractal", {
        "float frequency": [40],     
        "float amplitude": [120.0]     
    })

    ri.Displace("PxrDisplace", "carpetDisplace", {
        "reference float dispScalar": ["carpetFractal:resultF"],
        "float dispAmount": [0.4]       # Altura del desplazamiento
    })

    ri.Attribute("displacementbound", {"sphere": 1.0})

    # 3. Rug base material
    ri.Bxdf("PxrSurface", "carpetMaterial", {
        "color diffuseColor": [0.05, 0.1, 0.3],
        "float specularRoughness": [0.6] 
    })
    
    ri.Polygon({ri.P: [-50, 0, 50, 50, 0, 50, 50, 0, -50, -50, 0, -50]})
    ri.TransformEnd()
    ri.AttributeEnd()

    ################
    # DUMBBELL BAR
    ################

    ri.AttributeBegin()

    ri.Attribute("identifier", {"name":"bar"})
    ri.TransformBegin()
    
    # Axial line pattern
    ri.Pattern("PxrManifold2D", "cylindricalUV", {
        "int source": [1],         
        "float scaleS": [1.0],     
        "float scaleT": [800.0],   
    })

    # Pattern to simulate the lines
    ri.Pattern("PxrChecker", "linePattern", {
        "reference struct manifold": ["cylindricalUV:result"],
        "color colorA": [0.5, 0.5, 0.5], # Metal base
        "color colorB": [1.0, 1.0, 1.0],    # Lines color 
    })

    ri.Pattern("PxrBump", "lineBump", {
        "reference float inputBump": ["linePattern:resultR"],
        "float bumpHeight": [0.2], 
    })

    # Displacement config (Knurling)
    ri.Attribute("displacementbound", {"sphere": 1.0, "coordinatesystem": "shader"})
    ri.Attribute("dice", {"float micropolygonlength": [1.0]})

    # Displacement Pattern 
    ri.Pattern("KnurlingDisplacementMultiZone2", "KnurlingMultiZone", {
        "float scale": [0.1],
        "float frequency": [100.0],
        "float amplitude": [0.05],
        "float angle": [45.0],
    
        "float zone1_start": [-0.9],
        "float zone1_end": [-0.7],

        "float zone2_start": [-0.4],
        "float zone2_end": [0.7],

        "float zone3_start": [1.0],
        "float zone3_end": [1.2],
    })

    ri.Displace("PxrDisplace", "PxrDisplace", {
        "reference float dispScalar": ["KnurlingMultiZone:resultF"],
        "float dispAmount": [1.0]
    })

    # Fake bump neutral (To avoid displacement affect the surface of the bar without it)
    ri.Pattern("PxrBump", "fakeBump", {
        "float inputBump": [0.0],     
        "int bumpInterp": [1],       
        "float scale": [0.0]         
    })

    # Bar final material
    ri.Bxdf("PxrDisney", "barFinalMaterial", {
        "reference color baseColor": ["linePattern:resultRGB"],
        "float metallic": [1.0],
        "float roughness": [0.1],
        "reference normal bumpNormal": ["fakeBump:resultN"]
    })

    ri.ReadArchive("bar.rib")
    ri.TransformEnd()
    ri.AttributeEnd()

    #######################
    # DUMBBELL LEFT WEIGHT 
    #######################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "weight-left"})

    ri.Attribute("displacementbound", {"sphere": 1.0, "coordinatesystem": "shader"})

    # Base material 
    ri.Pattern("PxrFractal", "fractalPattern", {
        "float frequency": [60.0],
        "float amplitude": [20.0]
    })

    # PxrBump using fractal pattern result
    ri.Pattern("PxrBump", "bumpPattern", {
        "reference float inputBump": ["fractalPattern:resultF"],
        "float bumpHeight": [0.1],
        "int bumpType": [1]
    })
    
    # Bump Material (rough, matte surface with bump mapping)
    ri.Bxdf("PxrSurface", "bumpyMaterial", {
        "color diffuseColor": [0.05, 0.05, 0.05], 
        "reference normal bumpNormal": ["bumpPattern:resultN"],
        "float specularRoughness": [0.05]  
    })
    
    # Scratch Layer 1
    ri.Pattern("proceduralScratchRandom", "scratchLayer1", {
        "float scale": [1.9],
        "float thickness": [0.15],
        "float noiseAmount": [0.1],
        "float randomness": [30.0],
        "color scratchColor": [0.03, 0.03, 0.03],  
        "color baseColor": [0.05, 0.05, 0.05]
    })

     # Scratch Layer 2
    ri.Pattern("proceduralScratchRandom", "scratchLayer2", {
        "float scale": [1.0],
        "float thickness": [0.02],
        "float randomness": [0.2],
        "float rotation": [0.25],
        "color scratchColor": [0.03, 0.03, 0.03],
        "reference color baseColor": "scratchLayer1:result"
    })
    
    # Grunge para agregar negro a los bordes
    ri.Pattern("CurvatureBasedMix3", "grungeLayer", {
        "color edgeColor": [0.0, 0.0, 0.0],          
        "string curvatureMap": ["grunge.tex"],
        "float edgeMin": [0.1],
        "float edgeMax": [0.6],
        "reference color baseColor": ["scratchLayer2:result"] 
    })

    # Final dum shader
    ri.Bxdf("PxrSurface", "finalDumShader", {
        "reference color diffuseColor": ["grungeLayer:result"],
        "reference normal bumpNormal": ["bumpPattern:resultN"],
        "float specularRoughness": [0.05]
    })

    ri.ReadArchive("weight-left.rib")
    ri.AttributeEnd()

    # #########################
    # # DUMBBELL RIGHT WEIGHT
    # #########################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "dumbbell-right"})

    # Base material 
    ri.Pattern("PxrFractal", "fractalPattern", {
        "float frequency": [60.0],
        "float amplitude": [20.0]
    })

    # PxrBump using fractal pattern result
    ri.Pattern("PxrBump", "bumpPattern", {
        "reference float inputBump": ["fractalPattern:resultF"],
        "float bumpHeight": [0.1],
        "int bumpType": [1]
    })
    
    # Bump Material (rough, matte surface with bump mapping)
    ri.Bxdf("PxrSurface", "bumpyMaterial", {
        "color diffuseColor": [0.05, 0.05, 0.05], 
        "reference normal bumpNormal": ["bumpPattern:resultN"],
        "float specularRoughness": [0.05]  
    })

     # Scratch Layer 1
    ri.Pattern("proceduralScratchRandom", "scratchLayer1", {
        "float scale": [2.2],
        "float thickness": [0.15],
        "float noiseAmount": [0.1],
        "float randomness": [10.0],
        "color scratchColor": [0.03, 0.03, 0.03],  
        "color baseColor": [0.05, 0.05, 0.05]
    })

     # Scratch Layer 2
    ri.Pattern("proceduralScratchRandom", "scratchLayer2", {
        "float scale": [1.0],
        "float thickness": [0.05],
        "float randomness": [50.0],
        "float rotation": [0.25],
        "color scratchColor": [0.03, 0.03, 0.03],
        "reference color baseColor": "scratchLayer1:result"
    })
    
    # Grunge para agregar negro a los bordes
    ri.Pattern("CurvatureBasedMix3", "grungeLayer", {
        "color edgeColor": [0.0, 0.0, 0.0],          
        "string curvatureMap": ["grunge.tex"],
        "float edgeMin": [0.1],
        "float edgeMax": [0.6],
        "reference color baseColor": ["scratchLayer2:result"] 
    })

    # Final dum shader
    ri.Bxdf("PxrSurface", "finalDumShader", {
        "reference color diffuseColor": ["grungeLayer:result"],
        "reference normal bumpNormal": ["bumpPattern:resultN"],
        "float specularRoughness": [0.05]
    })
    
    ri.ReadArchive("weight-right.rib") 
    ri.AttributeEnd()

    ri.WorldEnd()
    ri.End()

if __name__ == "__main__":

    cl.ProcessCommandLine("testScenes.rib")

    parser = argparse.ArgumentParser(description="Modify render parameters")
 
    parser.add_argument(
        "--shadingrate",
        "-s",
        nargs="?",
        const=10.0,
        default=0.01,
        type=float,
        help="modify the shading rate default to 10",
    )
 
    parser.add_argument(
        "--pixelvar", "-p", nargs="?", const=0.001, default=0.0001, type=float, help="modify the pixel variance default  0.1"
    )
    parser.add_argument(
        "--fov", "-f", nargs="?", const=48.0, default=48.0, type=float, help="projection fov default 48.0"
    )
    parser.add_argument(
        "--width", "-wd", nargs="?", const=1024, default=1920, type=int, help="width of image default 1024"
    )
    parser.add_argument(
        "--height", "-ht", nargs="?", const=720, default=1080, type=int, help="height of image default 720"
    )
 
    parser.add_argument("--rib", "-r", action="count", help="render to rib not framebuffer")
    parser.add_argument("--default", "-d", action="count", help="use PxrDefault")
    parser.add_argument("--vcm", "-v", action="count", help="use PxrVCM")
    parser.add_argument("--direct", "-t", action="count", help="use PxrDirect")
    parser.add_argument("--wire", "-w", action="count", help="use PxrVisualizer with wireframe shaded")
    parser.add_argument("--normals", "-n", action="count", help="use PxrVisualizer with wireframe and Normals")
    parser.add_argument("--st", "-u", action="count", help="use PxrVisualizer with wireframe and ST")
 
    args = parser.parse_args()
 
 
    shadingrate = args.shadingrate if args.shadingrate is not None else 1.0
    pixelvar = args.pixelvar if args.pixelvar is not None else 0.01
    fov = args.fov if args.fov is not None else 48.0
    width = args.width if args.width is not None else 1024
    height = args.height if args.height is not None else 720
 
 
 
    if args.rib:
        filename = "domelight2.rib"
    else:
        filename = "__render"
 
    integratorParams = {}
    integrator = "PxrPathTracer"
    if args.default:
        integrator = "PxrDefault"
    if args.vcm:
        integrator = "PxrVCM"
    if args.direct:
        integrator = "PxrDirectLighting"
    if args.wire:
        integrator = "PxrVisualizer"
        integratorParams = {"int wireframe": [1], "string style": ["shaded"]}
    if args.normals:
        integrator = "PxrVisualizer"
        integratorParams = {"int wireframe": [1], "string style": ["normals"]}
    if args.st:
        integrator = "PxrVisualizer"
        integratorParams = {"int wireframe": [1], "string style": ["st"]}
 
    main(filename, args.shadingrate, args.pixelvar, args.fov, args.width, args.height, integrator, integratorParams)
 