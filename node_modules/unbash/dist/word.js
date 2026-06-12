function dequoteValue(parts) {
    let s = "";
    for (const c of parts)
        s += c.type === "Literal" ? c.value : c.text;
    return s;
}
export class WordImpl {
    static _resolveWord;
    static _resolveHeredocBody;
    text;
    pos;
    end;
    #source;
    #resolver;
    #parts;
    #value = null;
    constructor(text, pos, end, source, resolver) {
        this.text = text;
        this.pos = pos;
        this.end = end;
        this.#source = source ?? "";
        this.#resolver = resolver ?? WordImpl._resolveWord;
        this.#parts = source !== undefined ? null : undefined;
    }
    get value() {
        if (this.#value === null) {
            const parts = this.parts;
            if (!parts) {
                this.#value = this.text;
            }
            else {
                let s = "";
                for (const p of parts) {
                    switch (p.type) {
                        case "Literal":
                        case "SingleQuoted":
                        case "AnsiCQuoted":
                            s += p.value;
                            break;
                        case "DoubleQuoted":
                        case "LocaleString":
                            s += dequoteValue(p.parts);
                            break;
                        default:
                            s += p.text;
                            break;
                    }
                }
                this.#value = s;
            }
        }
        return this.#value;
    }
    get parts() {
        if (this.#parts === null) {
            this.#parts = this.#resolver(this.#source, this) ?? undefined;
        }
        return this.#parts;
    }
    set parts(v) {
        this.#parts = v ?? undefined;
    }
    toJSON() {
        return { text: this.text, pos: this.pos, end: this.end, parts: this.parts, value: this.value };
    }
}
