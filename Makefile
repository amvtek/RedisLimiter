vpath %.lua src

GENFUNC = tools/genfunc
FMT = stylua
OPTS = --indent-type Spaces --indent-width 4 --quote-style ForceDouble --syntax Lua51

lua_funcs :=  redis_limiter_funcs.lua
lua_scripts := sliding_window.lua
lua_sources := $(lua_scripts) $(lua_funcs)

.PHONY: lint tests format genfunc checkfunc clean

tests:
	python -m unittest -v

lint: $(lua_sources)
	$(FMT) --check $(OPTS) $^

checkfunc: build/checkfunc

genfunc: src/$(lua_funcs)

src/$(lua_funcs): $(lua_scripts)
	$(GENFUNC) > $@
	$(FMT) $(OPTS) $@

format: build/format

build/checkfunc: $(lua_sources)
	mkdir -p build
	$(GENFUNC) > build/$(lua_funcs)
	$(FMT) $(OPTS) build/$(lua_funcs)
	diff -q src/$(lua_funcs) build/$(lua_funcs)
	touch $@

build/format: $(lua_sources)
	mkdir -p build
	$(FMT) $(OPTS) $?
	touch $@

clean:
	rm -rf build
