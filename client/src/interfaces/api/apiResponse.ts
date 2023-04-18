export interface ApiResponse<Payload> {
    data: Payload;
    errors: Error[];
    status: number;
}

interface Error {
    kind: ErrorKind;
    message: string;
}

enum ErrorKind {
    InvalidJson,
    JsonValidationError,
    UniqueViolationError,
    RecordNotFoundError,
    CookieNotSet,
    CookieNotFound,
    UserAlreadyPresent,
    WrongPassword,
    IncorrectParameters,
    NewsSourceNotFound,
    ServerError,
}
