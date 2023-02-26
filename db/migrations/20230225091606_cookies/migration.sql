-- CreateTable
CREATE TABLE "UserCookies" (
    "id" INTEGER NOT NULL,
    "cookie" TEXT NOT NULL,
    "logged_in" BOOLEAN NOT NULL,

    CONSTRAINT "UserCookies_pkey" PRIMARY KEY ("cookie")
);

-- AddForeignKey
ALTER TABLE "UserCookies" ADD CONSTRAINT "UserCookies_id_fkey" FOREIGN KEY ("id") REFERENCES "Users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
