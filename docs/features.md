## Features

### Class Based Views

- Basic `View` and `APIView` classes for custom endpoints
- APIViews (async classes are prefixed with `Async`)
  - ListAPIView
  - CreateAPIView
  - RetrieveAPIView
  - UpdateAPIView
  - PartialUpdateAPIView
  - DestroyAPIView
- Generics with pluggable `Repository` interface, no dependency on ORM
- ViewSets 

## Helpers & Utils
- APIModel
- CamelCaseAPIModel
- Serializer - smart and fast serialization using `orjson`
- CamelCaseSerializer

- FastAPI app configuration & factory (via settings)
  - Openapi operation id simplification
  - Healthcheck
  - Prometheus metrics
  - error handlers
- Http Problem Details implementation

