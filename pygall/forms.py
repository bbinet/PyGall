from formalchemy import Grid, FieldSet
from fa.jquery import renderers as fa_renderers

FieldSet.default_renderers.update(fa_renderers.default_renderers)
