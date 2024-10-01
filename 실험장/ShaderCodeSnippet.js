code = /*wgsl*/ `
@group(0) @binding(0)
var<storage, read> uInputs: array < f32 >;

@group(0) @binding(1)
var<storage, read> vInputs: array < f32 >;

@group(0) @binding(2)
var<storage, read> cps: array < f32 >;

@group(0) @binding(3)
var<storage, read> knots: array < u32 >;

@group(0) @binding(4)
var<storage, read> uIntervals: array < u32 >;

@group(0) @binding(5)
var<storage, read> vIntervals: array < u32 >;

@group(0) @binding(6)
var<storage, read_write> output: array < u32 >;

@compute @workgroup_size(32)
fn main(@builtin(global_invocation_id) global_invocation_id: vec3u)
{
    let degree = % d;
    let cpsWidth = % d;
    let cpsHeight = % d;
    var uResult: array<vec2<f32>, cpsWidth>;

    // u 방향 b spline
    var tempIndex = uIntervals[gloval_invocation_id.x] + 1;

    let cpsNum = cpsWidth * cpsHeight;
    var tempCps = array < vec2 < f32 >, cpsNum>;

    var index = 0;
    while (index < cpsNum * 2) {
        tempCps[index].x = cps[index];
        tempCps[index].y = cps[index + 1];
        index += 2;
    }

    var height = 0;
    while (height * cpsWidth < cpsNum) {
        var tempArr: array<vec2<f32>, cpsNum>;

        for (var k = 1; k < degree + 1; ++k) {
            var a = 0;
            while (a < cpsNum) {
                tempArr[a] = vec2 < f32 > (0.0, 0.0);
                a += 2;
            }

            let iInitial = uinterval - degree + k + 1;

            for (var i = iInitial; i < interval + 2; ++i) {
                let alpha = (uInputs[gloval_invocation_id.x] - knots[i - 1]) / (knots[i + degree - k] - knots[i - 1]);

                temp[i] = (1 - alpha) * tempCps[i - 1 + height * cpsWidth] + alpha * tempCps[i + height * cpsWidth];
            }

            for (var i = 0; i < cpsWidth; ++i) {
                tempCps[i + height * cpsWidth] = temp[i];
            }
        }
        uResult[height] = tempCps[tempIndex + height * cpsWidth];
        ++height;
    }

    // v 방향 b spline
    var tempIndex = vIntervals[gloval_invocation_id.x] + 1;
}
`