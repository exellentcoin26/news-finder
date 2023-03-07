/*
  Warnings:

  - The primary key for the `RssEntries` table will be changed. If it partially fails, the table could be left without primary key constraint.

*/
-- AlterTable
ALTER TABLE "RssEntries" DROP CONSTRAINT "RssEntries_pkey",
ADD CONSTRAINT "RssEntries_pkey" PRIMARY KEY ("feed");
