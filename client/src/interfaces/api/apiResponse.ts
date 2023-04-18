export interface ApiResponse<Payload> {
    data?: Payload;
    errors: Error[];
    status: number;
}

export interface Error {
    kind: ErrorKind;
    message: string;
}

export enum ErrorKind {
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
