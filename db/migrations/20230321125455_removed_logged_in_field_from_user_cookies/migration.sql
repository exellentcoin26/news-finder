/*
  Warnings:

  - You are about to drop the column `id` on the `UserCookies` table. All the data in the column will be lost.
  - You are about to drop the column `logged_in` on the `UserCookies` table. All the data in the column will be lost.
  - Added the required column `user_id` to the `UserCookies` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "UserCookies" DROP CONSTRAINT "UserCookies_id_fkey";

-- AlterTable
ALTER TABLE "UserCookies" DROP COLUMN "id",
DROP COLUMN "logged_in",
ADD COLUMN     "user_id" INTEGER NOT NULL;

-- AddForeignKey
ALTER TABLE "UserCookies" ADD CONSTRAINT "UserCookies_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "Users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
