#!/usr/bin/env python3
"""Compare RAM map attribute preparation to the actual SGDK row routine."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from build_splash_v3_motion_lut import function


def main():
    project=Path(__file__).resolve().parents[1]
    workspace=next(p for p in project.parents if (p/'sdk/sgdk-2.11').is_dir())
    sdk=workspace/'sdk/sgdk-2.11'
    source=(project/'src/scenes/scene_branding_v3.c').read_text()
    library=(sdk/'src/vdp_tile.c').read_text()
    # The same signature is forward-declared near the top of vdp_tile.c.
    # Select the definition, not the prototype, before extracting its body.
    actual=function(library[library.rindex('static void prepareTileMapDataRowEx('):],
                    'prepareTileMapDataRowEx')
    helper=function(source,'v3PrepareLogoRowData')
    definitions=''
    for file,names in [('inc/vdp.h',['TILE_SIZE','TILE_INDEX_MASK']),
                       ('inc/vdp_tile.h',['TILE_ATTR_PRIORITY_SFT','TILE_ATTR_PALETTE_SFT','TILE_ATTR_VFLIP_SFT','TILE_ATTR_HFLIP_SFT','TILE_ATTR_PRIORITY_MASK','TILE_ATTR_PALETTE_MASK','TILE_ATTR_VFLIP_MASK','TILE_ATTR_HFLIP_MASK'])]:
        text=(sdk/file).read_text()
        for name in names:
            definitions+=re.search(r'^#define '+name+r'\s+[^\n]+',text,re.M)[0]+'\n'
    code='#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\ntypedef uint16_t u16;\n'+definitions+actual+'\n'+helper+r'''
int main(void){
    const u16 bases[]={0,0x2860,0xE7FF,0xF800,0xFFFF};
    u16 src[34],ref[34],fast[34];unsigned cases=0;
    for(unsigned base=0;base<5;base++)for(unsigned word=0;word<65536;word++){
        u16 width=(u16)(word%34);
        for(unsigned i=0;i<34;i++){src[i]=(u16)(word+i*37);ref[i]=fast[i]=0x3C3C;}
        prepareTileMapDataRowEx(ref,width,src,bases[base]);
        v3PrepareLogoRowData(fast,src,width,bases[base]);
        if(memcmp(ref,fast,sizeof(ref))){fprintf(stderr,"case %u mismatch\n",cases);return 1;}
        cases++;
    }
    printf("%u SGDK attribute-row cases passed: all source words, 5 bases, widths0..33 and tail guards\n",cases);return 0;
}
'''
    out=project/'rascunho/prepared_logo_map_20261016';out.mkdir(exist_ok=True)
    harness=out/'logo_map_differential.c';harness.write_text(code)
    subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(harness),'-o',str(out/'logo_map_differential')],check=True)
    result=subprocess.check_output([str(out/'logo_map_differential')],text=True).strip()
    report=dict(schema='splash_v3_logo_map_differential.v1',status='passed',cases=5*65536,
                sgdk_function_sha256=hashlib.sha256(actual.encode()).hexdigest(),helper_sha256=hashlib.sha256(helper.encode()).hexdigest(),
                source_sha256=hashlib.sha256(source.encode()).hexdigest(),result=result,
                scope='Row attributes and writes only. Runtime guards, original reveal timing, queued map identity and performance require ROM readback.')
    (project/'out/logs/splash_v3_logo_map_differential_20261016.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result)


if __name__=='__main__':main()
