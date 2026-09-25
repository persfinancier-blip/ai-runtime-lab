from __future__ import annotations

import ast
import inspect

from experiments.provider_generation_history import activation_schema


LAB090_TABLE_NAME = "provider_generation_activations"
LAB090_TABLE_SQL = """CREATE TABLE provider_generation_activations(
  activation_id TEXT PRIMARY KEY,
  new_generation_id TEXT NOT NULL UNIQUE,
  provider_id TEXT NOT NULL,
  generation INTEGER NOT NULL,
  expected_position INTEGER NOT NULL,
  fence INTEGER NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('SQL_COMMITTED','COMMITTED'))
)"""
LAB090_TRIGGER_NAME = "block_intent_during_provider_activation"
LAB090_TRIGGER_SQL = """CREATE TRIGGER block_intent_during_provider_activation
BEFORE INSERT ON shared_anchor_intents
WHEN EXISTS(
  SELECT 1 FROM provider_generation_activations WHERE status='SQL_COMMITTED'
)
BEGIN
  SELECT RAISE(ABORT, 'provider activation unresolved');
END"""


def test_activation_schema_exactly_matches_lab090_authority():
    assert activation_schema.ACTIVATION_TABLE_NAME == LAB090_TABLE_NAME
    assert activation_schema.ACTIVATION_TABLE_SQL == LAB090_TABLE_SQL
    assert activation_schema.ACTIVATION_TRIGGER_NAME == LAB090_TRIGGER_NAME
    assert activation_schema.ACTIVATION_TRIGGER_SQL == LAB090_TRIGGER_SQL
    assert activation_schema.normalized_sql("  SELECT\n  1   FROM x ") == "SELECT 1 FROM x"
    assert activation_schema.normalized_sql(LAB090_TABLE_SQL) == " ".join(LAB090_TABLE_SQL.split())
    assert activation_schema.normalized_sql(LAB090_TRIGGER_SQL) == " ".join(LAB090_TRIGGER_SQL.split())


def test_activation_schema_module_has_no_runtime_mutation_authority():
    tree = ast.parse(inspect.getsource(activation_schema))
    forbidden_calls = {
        "connect",
        "execute",
        "executemany",
        "commit",
        "rollback",
        "rotate",
        "increment",
        "store_receipt",
        "prepare_activation",
        "commit_activation",
        "release_activation",
    }
    observed_calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    observed_calls |= {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert forbidden_calls.isdisjoint(observed_calls)

    public = {name for name in vars(activation_schema) if not name.startswith("_")}
    assert public == {
        "annotations",
        "ACTIVATION_TABLE_NAME",
        "ACTIVATION_TABLE_SQL",
        "ACTIVATION_TRIGGER_NAME",
        "ACTIVATION_TRIGGER_SQL",
        "normalized_sql",
    }
