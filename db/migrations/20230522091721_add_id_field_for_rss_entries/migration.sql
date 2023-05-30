/*
  Warnings:

  - The primary key for the `RssEntries` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - A unique constraint covering the columns `[feed]` on the table `RssEntries` will be added. If there are existing duplicate values, this will fail.

*/
-- AlterTable
ALTER TABLE "RssEntries" DROP CONSTRAINT "RssEntries_pkey",
ADD COLUMN     "id" SERIAL NOT NULL,
ADD CONSTRAINT "RssEntries_pkey" PRIMARY KEY ("id");

-- CreateIndex
CREATE UNIQUE INDEX "RssEntries_feed_key" ON "RssEntries"("feed");
