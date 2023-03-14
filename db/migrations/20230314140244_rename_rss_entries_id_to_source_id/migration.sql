/*
  Warnings:

  - You are about to drop the column `id` on the `RssEntries` table. All the data in the column will be lost.
  - Added the required column `source_id` to the `RssEntries` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "RssEntries" DROP CONSTRAINT "RssEntries_id_fkey";

-- AlterTable
ALTER TABLE "RssEntries" RENAME COLUMN "id" TO "source_id";

-- AddForeignKey
ALTER TABLE "RssEntries" ADD CONSTRAINT "RssEntries_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "NewsSources"("id") ON DELETE CASCADE ON UPDATE CASCADE;
