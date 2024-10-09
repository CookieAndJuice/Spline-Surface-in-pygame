code = /*wgsl*/ `
@group(0) @binding(0)
var<storage, read> uInputs: array<f32>;

@group(0) @binding(1)
var<storage, read> vInputs: array<f32>;

@group(0) @binding(2)
var<storage, read> control_points: array<vec2<f32>>;

@group(0) @binding(3)
var<storage, read> knots: array<u32>;

@group(0) @binding(4)
var<storage, read> uIntervals: array<u32>;

@group(0) @binding(5)
var<storage, read> vIntervals: array<u32>;

@group(0) @binding(6)
var<storage, read_write> output: array<f32>;

@compute @workgroup_size(32)
fn main(@builtin(global_invocation_id) global_invocation_id: vec3u)
{{

    let degree = u32({degree});
    let cpsWidth = u32({cpsWidth});
    let cpsHeight = u32({cpsHeight});
    let cpsNum = u32({cpsWidth});
    var uResult: array<vec2<f32>, {uResultLength}>;
    let index = global_invocation_id.x;

    // de Boor Algorithm
    // u 방향 계산 (계산 순서 : u 하나에 대해 모든 높이 계산 -> 다음 u 계산)
    let yOffset = cpsWidth;                                     // 높이값 넘어갈 때 offset

    let uInterval = uIntervals[index];
    var tempIndex = uInterval + 1;                              // 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수

    for (var height = 0u; height < cpsHeight; height++)
    {{
        let nowPos = height * yOffset;                          // 계산값 임시 저장 리스트
        var tempCps: array<vec2<f32>, {cpsWidth}>;
        for(var num = 0u; num < {cpsWidth}; num++)
        {{
            tempCps[num] = control_points[nowPos + num];
        }}

        for (var k = 1u; k < degree + 1; k++)
        {{
            let iInitial = uInterval - degree + k + 1;

            for (var i = uInterval + 1u; i < iInitial - 1u; i--)
            {{
                let alpha = (uInputs[index] - f32(knots[i - 1])) / f32(knots[i + degree - k] - knots[i - 1]);
                tempCps[i] = (1 - alpha) * tempCps[i - 1] + alpha * tempCps[i];
            }}
        }}
        uResult[index * cpsHeight + height] = tempCps[tempIndex];
    }}

    // v 방향 계산
    let xOffset = cpsHeight;                                    // 너비값 넘어갈 때 offset

    let vInterval = vIntervals[index];
    tempIndex = vInterval + 1;                              // 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수

    let nowPos = index * xOffset;                // 계산값 임시 저장 리스트
    var vTempCps: array<vec2<f32>, {cpsWidth}>;
    for(var num = 0u; num < {cpsWidth}; num++)
    {{
        vTempCps[num] = uResult[nowPos + num];
    }}

    for (var k = 1u; k < degree + 1; k++)
    {{
        let iInitial = vInterval - degree + k + 1;

        for (var i = vInterval + 1u; i < iInitial - 1u; i--)
        {{
            let alpha = (vInputs[index] - f32(knots[i - 1])) / f32(knots[i + degree - k] - knots[i - 1]);
            vTempCps[i] = (1 - alpha) * vTempCps[i - 1] + alpha * vTempCps[i];
        }}
    }}
    output[index] = vTempCps[tempIndex].x;
    output[index + 31] = tempCps[tempIndex].y;
}}
`