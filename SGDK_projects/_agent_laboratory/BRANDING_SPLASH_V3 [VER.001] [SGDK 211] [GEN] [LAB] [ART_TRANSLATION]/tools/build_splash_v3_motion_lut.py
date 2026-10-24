#!/usr/bin/env python3
"""Bake numeric choreography from the unchanged C reference math, not pixels."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def function(source, name):
    start = re.search(r'static [^\n]+\b' + name + r'\(', source).start()
    brace = source.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--self-check', action='store_true')
    a = ap.parse_args()
    assert function('static s16 foo(void) { if (1) { return 3; } return 0; }\n', 'foo').endswith('return 0; }')
    if a.self_check:
        print('motion LUT extractor self-check passed (nested function body)')
        return
    project = Path(__file__).resolve().parents[1]
    source = (project / 'src/scenes/scene_branding_v3.c').read_text()
    parts = ['#include <stdint.h>\n#include <stdio.h>\ntypedef int8_t s8; typedef uint8_t u8; typedef int16_t s16; typedef uint16_t u16; typedef int32_t s32; typedef uint32_t u32;']
    for macro in ('SPLASH_PARTICLE_COUNT','SPLASH_SWEEP_SPARK_COUNT','SPLASH_ENERGY_START','SPLASH_OUTLINE_START','SPLASH_SGDK_X','SPLASH_SGDK_Y'):
        parts.append(re.search(r'^#define ' + macro + r'\s+\d+', source, re.M)[0])
    parts.append(re.search(r'typedef struct \{[^}]+\} SweepTrajectory;', source)[0])
    for array in ('sCos16','sSin16','sParticleTargetTileX','sParticleTargetTileY','sSweepTrajectories','sSweepNoisePx','sConvergeWeightQ16'):
        parts.append(re.findall(r'static const [^;]+?\b' + array + r'\[[^;]+?\n\};', source)[-1])
    parts.append('static s16 sParticleStartX[64], sParticleStartY[64];')
    for name in ('v3DivTowardZero','v3ParticleBirth','v3RadialPosition','v3ParticleTarget','v3ScaleQ16TowardZero','v3ParticlePosition','v3SweepEaseQ8','v3LerpQ8','v3BezierQ8','v3SweepPositionAt'):
        parts.append(function(source, name))
    reference = '\n\n'.join(parts)
    digest = hashlib.sha256(reference.encode()).hexdigest()
    run = project / 'rascunho/motion_lut_reference' / digest[:16]
    run.mkdir(parents=True, exist_ok=True)
    harness = reference + r'''
int main(void) {
    u16 i, f; s16 x, y;
    for (i=0; i<64; i++) v3RadialPosition(i,83,&sParticleStartX[i],&sParticleStartY[i]);
    for (f=24; f<120; f++) for (i=0; i<64; i++) {
        v3ParticlePosition(i,f,&x,&y); printf("%d %d\n",x,y);
    }
    for (i=0; i<6; i++) for (f=0; f<30; f++) {
        if (f<sSweepTrajectories[i].lifetimeFrames) v3SweepPositionAt(&sSweepTrajectories[i],f,&x,&y);
        else x=y=0;
        printf("%d %d\n",x,y);
    }
    return 0;
}
'''
    (run / 'reference.c').write_text(harness)
    subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror',str(run/'reference.c'),'-o',str(run/'reference')],check=True)
    output = subprocess.check_output([str(run/'reference')])
    (run / 'reference_positions.txt').write_bytes(output)
    positions = [tuple(map(int,line.split())) for line in output.decode().splitlines()]
    assert len(positions) == 96*64 + 6*30
    assert all(-32768 <= value <= 32767 for xy in positions for value in xy)
    # These independent endpoint bounds catch frame/particle order mistakes.
    assert positions[0] == (168,112)
    assert positions[96*64] == (-8,78)
    header = ['/* Generated numeric choreography; no graphics are authored here. */',
              '/* Reference math SHA-256: ' + digest + ' */',
              '#ifndef SPLASH_V3_MOTION_LUT_H', '#define SPLASH_V3_MOTION_LUT_H',
              'static const s16 sEnergyMotionLut[96][64][2] = {']
    for f in range(96):
        header.append('    {' + ','.join('{%d,%d}' % xy for xy in positions[f*64:(f+1)*64]) + '},')
    header.extend(['};','static const s16 sSweepMotionLut[6][30][2] = {'])
    for i in range(6):
        header.append('    {' + ','.join('{%d,%d}' % xy for xy in positions[96*64+i*30:96*64+(i+1)*30]) + '},')
    header.extend(['};','#endif',''])
    target = project / 'inc/generated/splash_v3_motion_lut.h'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text('\n'.join(header))
    report = dict(schema='splash_v3_motion_lut_generation.v1',reference_math_sha256=digest,
                  reference_c=str((run/'reference.c').relative_to(project)),
                  reference_positions=str((run/'reference_positions.txt').relative_to(project)),
                  header=str(target.relative_to(project)),header_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  coordinate_pairs=len(positions),rom_payload_bytes=len(positions)*4,
                  source='Unchanged integer C reference functions and r2 constants extracted from scene_branding_v3.c; compiled with fixed-width types.',
                  scope='Exact coordinate bake, geometry only; runtime equivalence and performance require a new ROM capture.')
    (project/'out/logs/splash_v3_motion_lut_generation_20261016.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
