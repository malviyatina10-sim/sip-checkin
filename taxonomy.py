"""Claude tagging output for the 300-item stratified sample (fixed taxonomy).
Format per line: sid relevant action triggers severity
action: C continuing | M missed (involuntary) | P paused | R reduced/withdrew | S stopped/left |
        K considering stopping/leaving | T starting/setup | N no SIP action stated
"""
RAW = """
S000 1 N UX 1
S001 1 N CM 2
S002 1 N - 1
S003 1 N - 1
S004 1 M PF 2
S005 1 N FL 1
S006 1 C - 1
S007 1 S PF,SW 3
S008 1 M PF,FE 3
S009 1 M PF,SUP 2
S010 1 N - 1
S011 1 N DS 1
S012 1 N UX 1
S013 1 M PF,SUP 2
S014 1 S SUP,UX 2
S015 1 S PF,SUP 3
S016 1 N FE 1
S017 1 S PF,SUP 3
S018 1 N - 1
S019 1 M PF,SUP 3
S020 1 K PF 2
S021 1 P MK,SUP 3
S022 1 N FL 2
S023 1 N FL 1
S024 1 S FL,SW 3
S025 0 N - 1
S026 1 N UX,SUP 2
S027 1 C - 1
S028 1 M PF,ON 3
S029 1 N FL 1
S030 0 N - 1
S031 1 N SUP 2
S032 1 N FL 1
S033 1 T ON 1
S034 1 N - 1
S035 1 N FL 1
S036 1 M PF 3
S037 1 C - 1
S038 1 T ON 1
S039 0 N - 1
S040 0 N - 1
S041 1 K FL 2
S042 1 M PF,SUP 2
S043 1 N UX,SUP 2
S044 0 N - 1
S045 1 M ON,PF 3
S046 1 S FE,SUP 2
S047 1 M PF 1
S048 0 N - 1
S049 1 N - 1
S050 1 K PF,SUP 2
S051 1 N SUP 2
S052 1 N FL 1
S053 1 S PF,FE,FL 3
S054 1 N GO 1
S055 1 T - 1
S056 1 S ON,SUP 2
S057 0 N - 1
S058 1 M PF,ON 2
S059 1 M ON,PF 3
S060 1 N UX 1
S061 1 M PF,ON 2
S062 1 S CM,SUP 3
S063 1 S PF,SUP 3
S064 1 N - 1
S065 1 N FL 2
S066 1 M PF,SUP 3
S067 1 K FL 2
S068 1 R CF 2
S069 1 M PF,SUP 3
S070 1 N - 1
S071 1 N FL 1
S072 1 C - 1
S073 1 S PF,SUP 3
S074 1 N - 1
S075 1 K FL,UX 3
S076 1 N - 1
S077 1 S FL,SW 3
S078 1 N PF,UX 2
S079 1 N PF 2
S080 1 N CM 1
S081 1 N - 1
S082 1 T ON,PF 3
S083 1 K FL,UX 2
S084 1 N - 1
S085 1 N - 1
S086 1 N FG 1
S087 1 N - 1
S088 1 N FL 1
S089 1 T ON 2
S090 1 N PF 3
S091 0 N - 1
S092 1 N CM 2
S093 1 N UX 1
S094 0 N - 1
S095 1 K FL 2
S096 1 S PF 3
S097 1 N ON,PF,UX 2
S098 1 S PF 3
S099 1 N UX 2
S100 0 N - 1
S101 1 N UX 1
S102 1 N GO,FL 1
S103 1 N CM 1
S104 1 N GO 1
S105 1 N GO 1
S106 0 N - 1
S107 0 N - 1
S108 1 N FL 1
S109 0 N - 1
S110 1 N FL,PF 2
S111 0 N - 1
S112 1 S PF,SUP 3
S113 0 N - 1
S114 1 S FL,SUP 3
S115 1 M PF,SUP 3
S116 1 N CM 1
S117 1 S PF,SUP 2
S118 1 T ON,SUP 2
S119 1 N - 1
S120 0 N - 1
S121 1 N CM 1
S122 0 N - 1
S123 1 T ON 2
S124 1 N UX 1
S125 0 N - 1
S126 1 N - 1
S127 1 N CM 2
S128 1 N - 1
S129 1 N SUP 3
S130 1 N UX 2
S131 1 C FL 1
S132 1 N FL 1
S133 1 T PF,UX 2
S134 1 N - 1
S135 1 C FL 1
S136 1 N CM 2
S137 1 N UX 1
S138 1 S CF,PF 3
S139 1 N GO,CM 1
S140 1 K UX 2
S141 1 N CM 2
S142 1 M UX,PF 2
S143 1 N UX 2
S144 1 M PF 3
S145 1 M PF,FL 2
S146 1 N FL,GO 1
S147 1 N DS 1
S148 1 S PF,UX 3
S149 1 N PF 2
S150 1 M PF 2
S151 1 M PF 2
S152 1 N GO 1
S153 1 N CM 1
S154 1 M PF,FE 3
S155 1 M PF,CF 2
S156 1 N GO,FL 1
S157 1 N FL 1
S158 1 N CM 1
S159 1 M PF 2
S160 1 K CM,SW 2
S161 1 M PF,DS 2
S162 1 N PF 2
S163 0 N - 1
S164 1 N CM,UX 1
S165 1 N PF 1
S166 1 S PF 3
S167 1 N PF 1
S168 1 N FL 1
S169 0 N - 1
S170 1 N PF 1
S171 1 N CM 1
S172 0 N - 1
S173 1 T ON,PF 2
S174 1 N CM 1
S175 1 M PF 2
S176 1 N UX 1
S177 1 N SUP 2
S178 1 N UX 2
S179 1 N UX 2
S180 1 M PF,SUP 3
S181 1 N GO 1
S182 1 M PF,FG 2
S183 1 N PF,UX 2
S184 1 M PF,CF 2
S185 1 N CF 1
S186 1 S FL,ON 3
S187 1 M PF 2
S188 1 N CM 1
S189 1 N DS 1
S190 1 N DS,GO 1
S191 1 N FL 1
S192 1 N CM 1
S193 1 N PF 1
S194 1 M PF 2
S195 1 M PF 2
S196 1 N CM 1
S197 1 K UX,SW 2
S198 1 N CM 1
S199 1 M PF,UX 2
S200 1 N OT 1
S201 1 N CM 1
S202 1 N SW 1
S203 1 N CM 1
S204 0 N - 1
S205 0 N - 1
S206 1 T ON 1
S207 1 K MK,RT,DS 3
S208 1 N PF 1
S209 1 M CF,FE 2
S210 1 N CM 1
S211 0 N - 1
S212 1 N CM 1
S213 1 N FL 1
S214 1 T ON,CM 1
S215 1 N DS 1
S216 0 N - 1
S217 0 N - 1
S218 0 N - 1
S219 1 N CM 2
S220 0 N - 1
S221 0 N - 1
S222 1 T CM 1
S223 0 N - 1
S224 1 N FL 1
S225 1 N CF,PF 2
S226 1 N FL 1
S227 1 C MK 1
S228 1 N CM,DS 1
S229 1 S ON 1
S230 0 N - 1
S231 1 K FL 2
S232 1 M CF,FE 2
S233 1 N CM 1
S234 1 N PF 1
S235 1 N CM 1
S236 1 N CM,PF 1
S237 0 N - 1
S238 0 N - 1
S239 0 N - 1
S240 0 N - 1
S241 1 N FL 1
S242 1 N OT 1
S243 1 N FL 1
S244 1 C MK 1
S245 1 T DS 1
S246 0 N - 1
S247 0 N - 1
S248 1 N FG 1
S249 1 C CM 1
S250 0 N - 1
S251 1 N CM 1
S252 0 N - 1
S253 1 N CM 1
S254 0 N - 1
S255 0 N - 1
S256 1 M PF 2
S257 1 P CF 2
S258 0 N - 1
S259 1 T FL 1
S260 1 N FL,CM 2
S261 1 N CM 1
S262 1 N CM 1
S263 1 N CM 1
S264 1 N CM 1
S265 0 N - 1
S266 1 T PF,CM 1
S267 0 N - 1
S268 1 N CM 1
S269 0 N - 1
S270 1 N CM 1
S271 1 N PF 1
S272 1 N CM 1
S273 1 N FL 1
S274 1 P FL 1
S275 1 K FL,CM 2
S276 1 N CM 1
S277 1 N CM 1
S278 1 N FL 1
S279 1 C DS 1
S280 1 K RT 2
S281 0 N - 1
S282 1 N CM 1
S283 0 N - 1
S284 0 N - 1
S285 1 N PF 1
S286 1 N CM 1
S287 1 M CF 1
S288 1 N PF 1
S289 1 C PF 1
S290 1 M CF,FE 3
S291 1 M CF 1
S292 1 N CM 1
S293 1 T CM 1
S294 1 N CM 1
S295 0 N - 1
S296 1 P CF,FL,FE 2
S297 1 P FL 1
S298 1 N CM 1
S299 0 N - 1
"""

TRIGGERS = {
    "PF": "Payment / mandate failure or friction",
    "CF": "Cash-flow: not enough balance on SIP date",
    "FE": "Bounce penalties / charges",
    "FL": "Can't easily skip / change date / amount",
    "CM": "Confusing returns metrics (XIRR, NAV, dashboard)",
    "DS": "Wants help deciding (continue / stop / what next)",
    "MK": "Market fall / news",
    "RT": "Disappointing returns",
    "FG": "Forgets / no reminder before SIP date",
    "ON": "Mandate / KYC setup trouble at start",
    "UX": "App bug / UX issue",
    "SUP": "Support failure",
    "SW": "Switching app / platform",
    "GO": "Wants goal tracking / projections",
    "OT": "Other",
}
ACTIONS = {"C": "continuing", "M": "missed (involuntary)", "P": "paused", "R": "reduced / withdrew",
           "S": "stopped / left", "K": "considering stopping", "T": "starting / setup", "N": "no action stated"}


def parse():
    out = {}
    for line in RAW.strip().splitlines():
        sid, rel, act, trig, sev = line.split()
        out[sid] = dict(relevant=int(rel), action=act,
                        triggers=[] if trig == "-" else trig.split(","), severity=int(sev))
    return out
