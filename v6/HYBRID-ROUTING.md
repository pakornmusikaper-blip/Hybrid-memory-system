# v6.2 External MiniMax Adapter + Hybrid Routing Policy

Status: Draft
Date: 2026-04-27

## Goal

Allow Substrate to choose between local and external models.

## Backends

- local Qwen adapter
- external MiniMax adapter
- heuristic fallback

## Routing dimensions

- privacy: restricted / normal
- budget: tight / normal / generous
- mode: light / standard / focused / reflect
- urgency: low / normal / high / immediate

## Default policy

- restricted privacy -> local
- tight budget -> local or heuristic
- focused/reflect + high urgency + generous budget -> external
- external failure -> local fallback -> heuristic fallback

## Why

This makes memory/token experiments real, not approximate.
