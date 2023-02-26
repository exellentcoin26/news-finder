-- DropIndex
DROP INDEX "UserLogins_id_key";

-- AlterTable
ALTER TABLE "UserLogins" ADD CONSTRAINT "UserLogins_pkey" PRIMARY KEY ("id");
