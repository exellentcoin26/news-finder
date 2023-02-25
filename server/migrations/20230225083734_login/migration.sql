-- CreateTable
CREATE TABLE "UserLogins" (
    "id" INTEGER NOT NULL,
    "password" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "UserLogins_id_key" ON "UserLogins"("id");

-- AddForeignKey
ALTER TABLE "UserLogins" ADD CONSTRAINT "UserLogins_id_fkey" FOREIGN KEY ("id") REFERENCES "Users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
